import logging
from abc import ABC, abstractmethod
from typing import List, Dict

class Player(ABC):
    """
    Abstract base class defining the interface for poker players.
    All concrete player implementations must inherit from this class.
    """
    def __init__(self, name: str, stack: int = 10000):
        """
        Initialize a new player.

        Args:
            name (str): The player's name
            stack (int, optional): Initial chip stack. Defaults to 10000.
        """
        self.name = name
        self.stack = stack
        self.hole_cards: List[str] = []
        self.folded = False
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)

    def reset_for_new_hand(self) -> None:
        """Reset player state for a new hand."""
        self.hole_cards.clear()
        self.folded = False

    @abstractmethod
    def request_action(
        self,
        community_cards: List[str],
        pot: int,
        call_amount: int,
        min_raise: int,
        game_history: str
    ) -> Dict:
        """
        Request an action from the player based on the current game state.

        Args:
            community_cards (List[str]): List of community cards
            pot (int): Current pot size
            call_amount (int): Amount needed to call
            min_raise (int): Minimum raise amount
            game_history (str): String representation of the game history

        Returns:
            Dict: Action dictionary with keys 'action' and 'raise_amount'
        """
        pass