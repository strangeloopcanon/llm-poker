# README.md
======================
poker_eval
----------

A minimal Python package that hosts a Texas Hold ’em environment so multiple LLMs can
play against each other. The environment handles:

1. Dealing: each player receives hole cards, community cards dealt in the standard sequence (flop, turn, river).
2. Action phases: we gather actions ("fold", "call", "raise") from each LLM in turn.
3. Basic reliability checks: we confirm that the actions returned by the LLM are valid.
   - If an invalid action is returned, we retry that LLM’s prompt.
4. Single-pot awarding: at showdown, the LLMs themselves decide who wins. The environment
   requests a JSON with the winner’s name. If there’s a tie, they should indicate a list
   of winners. If any contradiction occurs across LLM statements, it re-prompts them.

We skip blinds, side pots, advanced all-in logic, or actual system-level hand strength
evaluation. The LLMs will internally track their best hand, bluffing strategy, etc.
We simply ensure each action is legal and update the pot and call amount accordingly.

Install locally
---------------
git clone <this repo> poker_eval cd poker_eval pip install -e .


Example usage
-------------
Create a short script or interactive session:
```python
from poker_eval.game import simulate_poker_game

simulate_poker_game(
    model_names=["gpt-4o", "o1-pro", "claude-3.5-sonnet"],
    rounds=3,
    elimination_count=1
)
```

Check that you have configured your LLM keys properly using the llm CLI.

