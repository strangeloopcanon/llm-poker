import logging
logging.basicConfig(level=logging.WARNING)

from llm_poker.environment import simulate_poker_game

simulate_poker_game(
    model_names=[
        "gpt-5",
        "claude-4-sonnet",
        "gemini-2.5-pro",
        "deepseek-reasoner"
    ],
    rounds=5,
    elimination_count=0,
    starting_stack=10000,
    human_player=False
)
