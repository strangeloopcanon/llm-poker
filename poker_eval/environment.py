# poker_eval/environment.py

import random
import itertools
from typing import List, Dict
from .llm_player import LLMPlayer

RANKS = list(range(2, 15))  # 2..14 => 2..Ace
SUITS = ["♣", "♦", "♥", "♠"]


def create_deck() -> List[str]:
    return [f"{r}{s}" for r in RANKS for s in SUITS]

def deal(deck: List[str], n: int) -> List[str]:
    cards = deck[:n]
    del deck[:n]
    return cards

def card_rank(card: str) -> int:
    """Parse the rank portion (e.g. '14♥' => 14)."""
    # We find the first suit character, parse up to that as an int.
    for i, ch in enumerate(card):
        if ch in SUITS:
            return int(card[:i])
    return 0

def card_suit(card: str) -> str:
    """Parse the suit portion (e.g. '14♥' => '♥')."""
    for ch in card:
        if ch in SUITS:
            return ch
    return "?"


def score_best_5_of_7(cards: List[str]) -> tuple:
    """
    A simple 5-card evaluator for 7-card sets (2 hole + 5 board).
    Returns a tuple that can be compared to see who wins:
      (category, tiebreak...)
    where a bigger tuple is better.
    
    category order (roughly):
      8 = straight flush
      7 = four of a kind
      6 = full house
      5 = flush
      4 = straight
      3 = three of a kind
      2 = two pair
      1 = one pair
      0 = high card
    """
    # We'll generate all 5-card combinations, pick the best.
    # This is not the fastest approach for large scale, but it’s easy to read.
    
    def rank_5_cards(hand: List[str]) -> tuple:
        # hand is exactly 5 cards
        ranks = sorted([card_rank(c) for c in hand], reverse=True)
        suits = [card_suit(c) for c in hand]

        is_flush = (len(set(suits)) == 1)
        
        def is_straight(sorted_r: List[int]) -> bool:
            # check consecutive
            for i in range(len(sorted_r) - 1):
                if sorted_r[i] - sorted_r[i+1] != 1:
                    return False
            return True
        
        # Also handle the "5-4-3-2-A" special case if you want, but let's keep it simple.
        straight = is_straight(ranks)
        
        # Count duplicates
        from collections import Counter
        ccount = Counter(ranks)
        # sort by (count, rank) descending
        freq_sorted = sorted(ccount.items(), key=lambda x: (x[1], x[0]), reverse=True)
        # freq pattern e.g. [4,1], [3,2], [3,1,1], [2,2,1], ...
        freq_pattern = [x[1] for x in freq_sorted]
        rank_pattern = [x[0] for x in freq_sorted]
        
        # Determine category
        # 8 = straight flush, 7 = quads, 6 = full house, 5=flush, 4=straight
        # 3=trip, 2=two pair, 1=one pair, 0=high card
        cat = 0
        if straight and is_flush:
            cat = 8
        elif 4 in freq_pattern:
            cat = 7
        elif sorted(freq_pattern) == [2,3]:
            cat = 6
        elif is_flush:
            cat = 5
        elif straight:
            cat = 4
        elif 3 in freq_pattern:
            cat = 3
        else:
            # check for pairs
            pair_count = freq_pattern.count(2)
            if pair_count == 2:
                cat = 2
            elif pair_count == 1:
                cat = 1
            else:
                cat = 0
        
        # Return (category, freq_pattern, rank_pattern, sorted_r) as final tiebreak
        # The freq_pattern and rank_pattern help compare e.g. KKK72 vs QQQAK, etc.
        return (cat, freq_pattern, rank_pattern, ranks)
    
    best_val = (0, [], [], [])
    for combo in itertools.combinations(cards, 5):
        val = rank_5_cards(list(combo))
        if val > best_val:
            best_val = val
    return best_val


class PokerTable:
    """
    Minimal environment with forced blinds, internal showdown logic. 
    No side pots, no advanced all-in logic.
    """

    def __init__(
        self,
        players,
        min_raise: int = 100,
        small_blind: int = 50,
        big_blind: int = 100
    ):
        self.players = players
        self.min_raise = min_raise
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck: List[str] = []
        self.button_position = 0

    def play_hand(self) -> str:
        """
        1) Shuffle, reset players
        2) Post blinds
        3) Deal hole cards
        4) 4 betting rounds (preflop, flop, turn, river)
        5) If multiple remain -> showdown (use local scoring!)
        Returns history string
        """
        self.deck = create_deck()
        random.shuffle(self.deck)

        for p in self.players:
            p.reset_for_new_hand()

        history = f"=== NEW HAND (button at seat {self.button_position+1}) ==="
        for p in self.players:
            if p.stack <= 0:
                p.folded = True

        # hole cards
        for p in self.players:
            if p.stack > 0:
                p.hole_cards = deal(self.deck, 2)

        pot = 0
        call_amount = 0
        community_cards: List[str] = []

        # post blinds
        def seat_idx(offset):
            return (self.button_position + 1 + offset) % len(self.players)

        sb_idx = seat_idx(0)
        bb_idx = seat_idx(1)
        
        sb_p = self.players[sb_idx]
        sb_amt = min(self.small_blind, sb_p.stack)
        sb_p.stack -= sb_amt
        pot += sb_amt
        history += f"\n{sb_p.name} posts SB {sb_amt}."

        bb_p = self.players[bb_idx]
        bb_amt = min(self.big_blind, bb_p.stack)
        bb_p.stack -= bb_amt
        pot += bb_amt
        history += f"\n{bb_p.name} posts BB {bb_amt}."

        call_amount = bb_amt

        def run_betting_round(stage_name: str):
            nonlocal pot, call_amount, history
            seats_in_order = [
                (bb_idx + 1 + i) % len(self.players)
                for i in range(len(self.players))
            ]
            for seat in seats_in_order:
                ply = self.players[seat]
                if ply.folded or ply.stack <= 0:
                    continue
                
                action_info = ply.request_action(
                    community_cards=community_cards,
                    pot=pot,
                    call_amount=call_amount,
                    min_raise=self.min_raise,
                    game_history=history + f"\n(betting round: {stage_name}, seat={seat+1})"
                )
                act = action_info["action"]
                ramt = action_info["raise_amount"]

                if act == "fold":
                    ply.folded = True
                    history += f"\n{ply.name} folds."
                elif act == "call":
                    # must pay call_amount
                    if ply.stack < call_amount:
                        # can't match => fold
                        ply.folded = True
                        history += f"\n{ply.name} tries calling {call_amount} but lacks chips => folds."
                    else:
                        ply.stack -= call_amount
                        pot += call_amount
                        history += f"\n{ply.name} calls {call_amount}."
                elif act == "raise":
                    desired = ramt if ramt else (call_amount + self.min_raise)
                    minimum_needed = call_amount + self.min_raise
                    if desired < minimum_needed:
                        desired = minimum_needed
                    if desired > ply.stack:
                        # can't afford
                        ply.folded = True
                        history += f"\n{ply.name} tries raising to {desired} but lacks chips => folds."
                    else:
                        ply.stack -= desired
                        pot += desired
                        call_amount = desired
                        history += f"\n{ply.name} raises total to {desired}."

        # preflop
        run_betting_round("preflop")
        active = [p for p in self.players if not p.folded and p.stack > 0]

        # flop
        if len(active) > 1:
            flop_cards = deal(self.deck, 3)
            community_cards.extend(flop_cards)
            history += f"\nFLOP: {flop_cards}"
            run_betting_round("flop")
            active = [p for p in active if not p.folded and p.stack > 0]

        # turn
        if len(active) > 1:
            turn_card = deal(self.deck, 1)
            community_cards.extend(turn_card)
            history += f"\nTURN: {turn_card}"
            run_betting_round("turn")
            active = [p for p in active if not p.folded and p.stack > 0]

        # river
        if len(active) > 1:
            river_card = deal(self.deck, 1)
            community_cards.extend(river_card)
            history += f"\nRIVER: {river_card}"
            run_betting_round("river")
            active = [p for p in active if not p.folded and p.stack > 0]

        # showdown or single winner
        if len(active) == 1:
            winner = active[0]
            winner.stack += pot
            history += f"\nOnly {winner.name} remains, wins pot of {pot}."
            pot = 0
        elif len(active) == 0:
            # everyone folded at some point => pot unclaimed
            history += "\nAll folded => pot unclaimed."
        else:
            # multiple remain => local showdown
            best_val = None
            winners = []
            for p in active:
                # 7 cards: p.hole_cards + community_cards
                combined = p.hole_cards + community_cards
                val = score_best_5_of_7(combined)
                if best_val is None or val > best_val:
                    best_val = val
                    winners = [p]
                elif val == best_val:
                    winners.append(p)
            
            if len(winners) == 1:
                w = winners[0]
                w.stack += pot
                history += f"\nShowdown: {w.name} wins pot of {pot}."
                pot = 0
            else:
                # tie => chop pot
                share = pot // len(winners)
                for w in winners:
                    w.stack += share
                history += f"\nShowdown tie among {[w.name for w in winners]}. Each gets {share}."
                pot = 0

        # rotate button
        self.button_position = (self.button_position + 1) % len(self.players)
        return history

    def remove_busted(self):
        for p in self.players:
            if p.stack <= 0:
                p.folded = True


def simulate_poker_game(
    model_names: List[str],
    rounds: int = 5,
    elimination_count: int = 1,
    starting_stack: int = 10000
):
    """
    1) Build LLMPlayers from the model_names
    2) Seat them at a PokerTable
    3) Print out each hand's action log
    4) Compare final stacks
    """
    from .llm_player import LLMPlayer

    players = []
    for i, m_name in enumerate(model_names):
        p = LLMPlayer(name=f"Player_{i+1}", model_id=m_name, stack=starting_stack)
        players.append(p)

    table = PokerTable(players=players, min_raise=100, small_blind=50, big_blind=100)

    for _round in range(rounds):
        alive = sum(not pl.folded and pl.stack > 0 for pl in players)
        if alive <= elimination_count:
            break

        history = table.play_hand()
        print(history, "\n----- END HAND -----\n")
        table.remove_busted()

    # final standings
    rank = sorted(players, key=lambda x: x.stack, reverse=True)
    print("\n=== FINAL STANDINGS ===")
    for i, r in enumerate(rank, start=1):
        print(f"{i}. {r.name} ({r.model_id}): ${r.stack}")
