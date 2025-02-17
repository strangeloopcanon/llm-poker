# llm_poker/environment.py

import random
import itertools
from typing import List, Dict
from .llm_player import LLMPlayer
from .human_player import HumanPlayer

RANKS = list(range(2, 15))  # 2..14 => 2..Ace
SUITS = ["♣", "♦", "♥", "♠"]

def create_deck() -> List[str]:
    return [f"{r}{s}" for r in RANKS for s in SUITS]

def deal(deck: List[str], n: int) -> List[str]:
    cards = deck[:n]
    del deck[:n]
    return cards

def card_rank(card: str) -> int:
    # e.g. '14♥' => 14
    for i, ch in enumerate(card):
        if ch in SUITS:
            return int(card[:i])
    return 0

def card_suit(card: str) -> str:
    # e.g. '14♥' => '♥'
    for ch in card:
        if ch in SUITS:
            return ch
    return "?"


def score_best_5_of_7(cards: List[str]) -> tuple:
    """
    Minimal 7->5 card evaluator returning a comparable tuple: (category, freq_pattern, rank_pattern, sorted_ranks).
    8=straight flush, 7=quads, 6=full house, 5=flush, 4=straight,
    3=trips, 2=two pair, 1=pair, 0=high card.
    """
    import itertools
    from collections import Counter

    def rank_5_cards(hand: List[str]) -> tuple:
        ranks = sorted([card_rank(c) for c in hand], reverse=True)
        suits = [card_suit(c) for c in hand]
        is_flush = (len(set(suits)) == 1)

        def is_straight(sorted_r: List[int]) -> bool:
            for i in range(len(sorted_r) - 1):
                if sorted_r[i] - sorted_r[i+1] != 1:
                    return False
            return True

        straight = is_straight(ranks)

        ccount = Counter(ranks)
        freq_sorted = sorted(ccount.items(), key=lambda x: (x[1], x[0]), reverse=True)
        freq_pattern = [x[1] for x in freq_sorted]
        rank_pattern = [x[0] for x in freq_sorted]

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
            pair_count = freq_pattern.count(2)
            if pair_count == 2:
                cat = 2
            elif pair_count == 1:
                cat = 1
            else:
                cat = 0

        return (cat, freq_pattern, rank_pattern, ranks)

    best_val = (0, [], [], [])
    for combo in itertools.combinations(cards, 5):
        val = rank_5_cards(list(combo))
        if val > best_val:
            best_val = val
    return best_val


class PokerTable:
    """
    Minimal environment with blinds, multi-raise logic, local showdown scoring.
    No side pots or advanced all-in tracking beyond forced folding if short.
    """

    def __init__(self, players, min_raise=500, small_blind=100, big_blind=200):
        self.players = players
        self.min_raise = min_raise
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck: List[str] = []
        self.button_position = 0

    def play_hand(self) -> str:
        """
        Shuffle, post blinds, deal 2 hole cards, then 4 betting rounds
        with multiple re-raises, ending in showdown if needed.
        """
        self.deck = create_deck()
        random.shuffle(self.deck)

        # reset
        for p in self.players:
            p.reset_for_new_hand()

        history = f"=== NEW HAND (button at seat {self.button_position+1}) ==="
        for p in self.players:
            if p.stack <= 0:
                p.folded = True

        # Deal hole cards
        for p in self.players:
            if p.stack > 0:
                p.hole_cards = deal(self.deck, 2)
                history += f"\n{p.name} hole cards: {p.hole_cards}"

        pot = 0
        community_cards: List[str] = []

        # Post blinds
        def seat_idx(offset):
            return (self.button_position + 1 + offset) % len(self.players)

        sb_idx = seat_idx(0)
        bb_idx = seat_idx(1)

        sb_player = self.players[sb_idx]
        bb_player = self.players[bb_idx]

        sb_amt = min(self.small_blind, sb_player.stack)
        bb_amt = min(self.big_blind, bb_player.stack)

        sb_player.stack -= sb_amt
        pot += sb_amt
        history += f"\n{sb_player.name} posts SB {sb_amt}."

        bb_player.stack -= bb_amt
        pot += bb_amt
        history += f"\n{bb_player.name} posts BB {bb_amt}."

        call_amount = bb_amt

        def run_betting_round(stage_name: str):
            nonlocal pot, call_amount, history

            # Gather active seats in standard seat order (start from sb->bb->etc).
            # We'll define a circular list starting from the first to act (i.e., seat after big blind).
            seats_in_order = []
            total_players = len(self.players)
            start_seat = (bb_idx + 1) % total_players
            for i in range(total_players):
                seats_in_order.append((start_seat + i) % total_players)

            # Filter out folded or busted
            active_seats = [
                s for s in seats_in_order
                if (not self.players[s].folded and self.players[s].stack > 0)
            ]

            if not active_seats:
                return  # Everyone folded or broke

            # We'll track how many players have acted since the last raise.
            # Once we pass all active players with no new raise, the betting ends.
            current_highest_bet = call_amount
            players_acted_since_raise = 0
            idx = 0

            while True:
                # If only 1 seat remains, break
                if len(active_seats) < 2:
                    break

                seat = active_seats[idx]
                ply = self.players[seat]
                if ply.folded or ply.stack <= 0:
                    # remove them from active seats
                    active_seats.remove(seat)
                    if idx >= len(active_seats):
                        idx = 0
                    if len(active_seats) < 2:
                        break
                    continue

                # prompt LLM for action
                game_state = history + f"\n(betting round: {stage_name}, seat={seat+1})"
                action_info = ply.request_action(
                    community_cards=community_cards,
                    pot=pot,
                    call_amount=current_highest_bet,
                    min_raise=self.min_raise,
                    game_history=game_state
                )
                act = action_info["action"]
                ramt = action_info["raise_amount"]

                if act == "fold":
                    ply.folded = True
                    history += f"\n{ply.name} folds."
                    active_seats.remove(seat)
                    if len(active_seats) < 2:
                        break
                    # do not advance idx in case we removed the current seat
                    if idx >= len(active_seats):
                        idx = 0
                    continue

                elif act == "call":
                    diff = current_highest_bet
                    if ply.stack < diff:
                        # can't match => fold
                        ply.folded = True
                        history += f"\n{ply.name} tries calling {diff} but lacks chips => folds."
                        active_seats.remove(seat)
                        if len(active_seats) < 2:
                            break
                        if idx >= len(active_seats):
                            idx = 0
                        continue
                    else:
                        ply.stack -= diff
                        pot += diff
                        history += f"\n{ply.name} calls {diff}."
                        players_acted_since_raise += 1

                elif act == "raise":
                    desired_total = ramt if ramt else (current_highest_bet + self.min_raise)
                    minimum_needed = current_highest_bet + self.min_raise
                    if desired_total < minimum_needed:
                        desired_total = minimum_needed

                    if desired_total > ply.stack:
                        # can't afford that raise => fold
                        ply.folded = True
                        history += f"\n{ply.name} tries raising to {desired_total} but lacks chips => folds."
                        active_seats.remove(seat)
                        if len(active_seats) < 2:
                            break
                        if idx >= len(active_seats):
                            idx = 0
                        continue
                    else:
                        # Must pay desired_total
                        ply.stack -= desired_total
                        pot += desired_total
                        current_highest_bet = desired_total
                        history += f"\n{ply.name} raises total to {desired_total}."
                        players_acted_since_raise = 0  # reset because new raise

                # move to next seat
                idx = (idx + 1) % len(active_seats)

                # if we've gone around the table with no new raise, end
                if players_acted_since_raise >= len(active_seats):
                    break

        # ********** PRE-FLOP **********
        run_betting_round("preflop")
        active = [p for p in self.players if not p.folded and p.stack > 0]

        # ********** FLOP **********
        if len(active) > 1:
            flop_cards = deal(self.deck, 3)
            community_cards.extend(flop_cards)
            history += f"\nFLOP: {flop_cards}"
            run_betting_round("flop")
            active = [p for p in active if not p.folded and p.stack > 0]

        # ********** TURN **********
        if len(active) > 1:
            turn_card = deal(self.deck, 1)
            community_cards.extend(turn_card)
            history += f"\nTURN: {turn_card}"
            run_betting_round("turn")
            active = [p for p in active if not p.folded and p.stack > 0]

        # ********** RIVER **********
        if len(active) > 1:
            river_card = deal(self.deck, 1)
            community_cards.extend(river_card)
            history += f"\nRIVER: {river_card}"
            run_betting_round("river")
            active = [p for p in active if not p.folded and p.stack > 0]

        # Check for single winner or showdown
        pot_before_showdown = pot
        if len(active) == 1:
            winner = active[0]
            winner.stack += pot
            history += f"\nOnly {winner.name} remains, wins pot of {pot}."
            pot = 0
        elif len(active) == 0:
            history += "\nAll folded => pot unclaimed."
        else:
            # multiple remain => showdown
            best_val = None
            winners = []
            for p in active:
                combined = p.hole_cards + community_cards
                history += f"\nAt showdown, {p.name} hole cards: {p.hole_cards}"
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
                share = pot // len(winners)
                names = [ww.name for ww in winners]
                for ww in winners:
                    ww.stack += share
                history += f"\nShowdown tie among {names}; each gets {share}."
                pot = 0

        # Rotate dealer button
        self.button_position = (self.button_position + 1) % len(self.players)
        return history

    def remove_busted(self):
        # Mark folded anyone with 0 chips
        for p in self.players:
            if p.stack <= 0:
                p.folded = True


def simulate_poker_game(
    model_names: List[str],
    rounds: int = 5,
    elimination_count: int = 1,
    starting_stack: int = 10000,
    human_player: bool = False
):
    """
    1) Build LLMPlayers
    1a) If human_player=True, add a HumanPlayer
    2) Seat them at the multi-raise PokerTable
    3) Print each hand's log
    4) Print final standings
    """

    players = []
    for i, m_name in enumerate(model_names):
        p = LLMPlayer(name=f"Player_{i+1}", model_id=m_name, stack=starting_stack)
        players.append(p)

    if human_player:
        # Create a human player and insert it into the list of players at a random position
        random_position = random.randint(0, len(players))   
        players.insert(random_position, HumanPlayer(name="Human", stack=starting_stack))

    table = PokerTable(players=players, min_raise=500, small_blind=50, big_blind=100)

    for _round in range(rounds):
        alive = sum(not pl.folded and pl.stack > 0 for pl in players)
        if alive <= elimination_count:
            break

        hand_history = table.play_hand()
        print(hand_history, "\n----- END HAND -----\n")
        table.remove_busted()

    # final standings
    ranking = sorted(players, key=lambda x: x.stack, reverse=True)
    print("\n=== FINAL STANDINGS ===")
    for i, ply in enumerate(ranking, start=1):
        print(f"{i}. {ply.name} ({ply.model_id}): ${ply.stack}")
