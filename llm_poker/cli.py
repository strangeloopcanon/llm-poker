# llm_poker/cli.py

import click
from llm_poker.environment import simulate_poker_game

@click.command()
@click.option("--models", "-m", default="gpt-5", help="Space-separated model names.")
@click.option("--rounds", "-r", default=3, help="Number of rounds/hands to deal.")
@click.option("--elimination-count", "-e", default=1, help="Stop when only this many players remain.")
@click.option("--stack", "-s", default=10000, help="Starting stack for each player.")
@click.option("--human-player", "-h", is_flag=True, help="Whether to include a human player", default=False)
def main(models, rounds, elimination_count, stack, human_player):
    """
    CLI to run a multi-LLM Texas Hold'em simulation.
    Example:
      llm_poker --models gpt-4o deepseek-chat --rounds 5
    """
    model_list = models.strip().split()
    # If user doesn’t supply anything, fall back to a modern default
    if not model_list:
        model_list = ["gpt-5"]

    simulate_poker_game(
        model_names=model_list,
        rounds=rounds,
        elimination_count=elimination_count,
        starting_stack=stack,
        human_player=human_player,
    )

if __name__ == "__main__":
    main()
