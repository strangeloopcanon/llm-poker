import logging
logging.basicConfig(level=logging.INFO)

from poker_eval.environment import simulate_poker_game

simulate_poker_game(
    model_names=["gpt-4o", "claude-3-5-haiku-latest", "claude-3-5-sonnet-latest", "deepseek-chat"],
    rounds=5,
    elimination_count=0,
    starting_stack=10000,
    min_raise = 500
)
