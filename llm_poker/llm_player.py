# llm_player.py

import json
from typing import List, Dict, Optional, Type
import llm
from pydantic import BaseModel, ValidationError, Field
from .player import Player

class ActionSchema(BaseModel):
    action: str = Field(..., pattern="^(fold|call|raise)$")
    raise_amount: Optional[int] = None

class ShowdownSchema(BaseModel):
    winner_names: List[str]

def extract_json_snippet(text: str) -> str:
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in output.")
    return text[start:end+1]

def parse_llm_json(raw_text: str, model_class: Type[BaseModel]) -> BaseModel:
    """
    1) Extract JSON snippet from raw_text
    2) Parse that snippet as JSON
    3) Instantiate the provided pydantic model_class with the parsed dict
    4) Return the validated object
    """
    snippet = extract_json_snippet(raw_text)
    data = json.loads(snippet)
    return model_class(**data)

#######################################################################

class LLMPlayer(Player):
    """
    A poker player implementation that uses an LLM to make decisions.
    """
    def __init__(self, name: str, model_id: str, stack: int = 10000):
        """
        Initialize an LLM-based poker player.

        Args:
            name (str): The player's name
            model_id (str): ID of the LLM model to use
            stack (int, optional): Initial chip stack. Defaults to 10000.
        """
        super().__init__(name, stack)
        self.model_id = model_id
        self._model = llm.get_model(model_id)

    def request_action(
        self,
        community_cards: List[str],
        pot: int,
        call_amount: int,
        min_raise: int,
        game_history: str
    ) -> Dict:
        """
        Request an action from the LLM player based on the current game state.

        Args:
            community_cards (List[str]): List of community cards
            pot (int): Current pot size
            call_amount (int): Amount needed to call
            min_raise (int): Minimum raise amount
            game_history (str): String representation of the game history

        Returns:
            Dict: Action dictionary with keys 'action' and 'raise_amount'
            
        Raises:
            RuntimeError: If the LLM gives too many invalid responses
        """
        prompt_text = f"""
You are an expert-level poker AI tasked with making optimal decisions in a poker game. Your job is to WIN! WIN! You will be given the current game state and your goal is to determine the best action to take.

Here's the current game state:

Game history: {game_history}
You are {self.name} with {self.stack} chips.

Hole cards: {self.hole_cards}
Community cards: {community_cards}
Pot: {pot}
Amount to call: {call_amount}
Minimum raise over current call: {min_raise}

Instructions:
1. Analyze the given information carefully.
2. Consider advanced poker concepts such as position, pot odds, implied odds, and opponent tendencies.
3. Determine the optimal action: fold, call, or raise.
4. If raising, calculate an appropriate raise amount.
5. Output your decision in valid JSON format.

Important rules:
- If the amount to call is 0, use "call" to represent a check.
- Never output "check" as an action. Only use fold/call/raise.
- Ensure your output is in valid JSON format.

Before making your final decision, wrap your thought process inside <poker_reasoning> tags. Consider the following aspects:
- Evaluate hand strength using standard poker hand rankings
- Calculate pot odds and compare them to the required call amount
- Analyze position and betting patterns
- Consider opponent tendencies based on game history
- Perform a risk/reward analysis of different actions (fold, call, raise)

After your analysis, provide your final decision in JSON format with two keys:
- "action": Either "fold", "call", or "raise"
- "raise_amount": An integer value if raising, or null if not raising

Example output structure (do not copy this content, only the structure):
<poker_reasoning>
[Detailed reasoning of the poker situation]
</poker_reasoning>

Now, analyze the current game state and make your expert-level poker decision.
Output VALID JSON ONLY, e.g.:
{{
  "action": "call",
  "raise_amount": null
}}
        """

        for attempt in range(5): # Should be while True: but changed to not have infinite loops.
            resp = self._model.prompt(prompt_text)
            raw_text = resp.text().strip()
            self.logger.debug(f"Raw LLM action output (attempt {attempt+1}): {raw_text!r}")

            try:
                data = parse_llm_json(raw_text, ActionSchema)
                # data is a validated ActionSchema object
                return data.dict()  # or just return data if you prefer
            except (ValueError, ValidationError) as e:
                self.logger.warning(f"Parsing/validation error on attempt {attempt+1}: {e}")

        raise RuntimeError(f"{self.name} gave too many invalid responses for request_action")
