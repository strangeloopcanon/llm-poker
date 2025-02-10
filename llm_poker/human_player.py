from typing import Dict, List
from .player import Player

class HumanPlayer(Player):
    """
    A human player implementation that interacts through the command line.
    Inherits from the Player base class and implements interactive decision making.
    """

    def __init__(self, name: str, stack: int = 10000):
        """
        Initialize a new human player.

        Args:
            name (str): The player's name
            stack (int, optional): Initial chip stack. Defaults to 10000.
        """
        super().__init__(name, stack)
        self.model_id: str = "Human"
    
    def request_action(
        self,
        community_cards: List[str],
        pot: int,
        call_amount: int,
        min_raise: int,
        game_history: str
    ) -> Dict:
        """
        Request an action from the human player through command line input.

        Args:
            community_cards (List[str]): List of community cards
            pot (int): Current pot size
            call_amount (int): Amount needed to call
            min_raise (int): Minimum raise amount
            game_history (str): String representation of the game history

        Returns:
            Dict: Action dictionary with keys 'action' and optionally 'raise_amount'
        """
        # Display current game state
        print("\n=== Your Turn ===")
        print(f"Your hole cards: {self.hole_cards}")
        print(f"Community cards: {community_cards}")
        print(f"Current pot: {pot}")
        print(f"Amount to call: {call_amount}")
        print(f"Minimum raise: {min_raise}")
        print(f"Your stack: {self.stack}")
        print("\nGame history:")
        print(game_history)

        while True:
            # Get player action
            print("\nAvailable actions:")
            print("1. fold")
            print("2. call")
            print("3. raise")
            action = input("\nEnter your action (1/2/3): ").strip().lower()

            if action in ['1', 'fold']:
                return {'action': 'fold', 'raise_amount': None}
            elif action in ['2', 'call']:
                return {'action': 'call', 'raise_amount': None}
            elif action in ['3', 'raise']:
                while True:
                    try:
                        raise_amount = int(input(f"Enter raise amount (minimum {min_raise}): "))
                        if raise_amount < min_raise:
                            print(f"Raise amount must be at least {min_raise}")
                            continue
                        if raise_amount > self.stack:
                            print(f"You cannot raise more than your stack ({self.stack})")
                            continue
                        return {'action': 'raise', 'raise_amount': raise_amount}
                    except ValueError:
                        print("Please enter a valid number")
            else:
                print("Invalid action. Please try again.")