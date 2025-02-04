# poker_eval/cli.py

import click
from .environment import simulate_poker_game

@click.command()
@click.option("--models", "-m", multiple=True, default=["gpt-4o"], help="LLM model names, can use multiple.")
@click.option("--rounds", "-r", default=3, help="Number of rounds/hands to deal.")
@click.option("--elimination-count", "-e", default=1, help="Stop when only this many players remain.")
@click.option("--stack", "-s", default=10000, help="Starting stack for each player.")
def main(models, rounds, elimination_count, stack):
    """
    CLI to run a multi-LLM Texas Hold'em simulation.
    Example:
      poker-eval --models gpt-4o --models deepseek-chat --rounds 5
    """
    simulate_poker_game(
        model_names=list(models),
        rounds=rounds,
        elimination_count=elimination_count,
        starting_stack=stack,
        min_raise=100
    )

if __name__ == "__main__":
    main()
