'''
    File name: five_hundred/judger.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game import FiveHundredGame

from .utils.action_event import PlayCardAction
from .utils.action_event import ActionEvent, BidAction, PassAction
from .utils.move import MakeBidMove
from .utils.five_hundred_card import FiveHundredCard


class FiveHundredJudger:
    '''
        Judger decides legal actions for current player
    '''

    def __init__(self, game: 'FiveHundredGame'):
        ''' Initialize the class FiveHundredJudger
        :param game: FiveHundredGame
        '''
        self.game: FiveHundredGame = game
        self.led_suits = []

    def reset(self):
        self.led_suits = []

    def get_legal_actions(self) -> List[ActionEvent]:
        """
        :return: List[ActionEvent] of legal actions
        """
        legal_actions: List[ActionEvent] = []
        if not self.game.is_over():
            current_player = self.game.round.get_current_player()
            if not self.game.round.is_bidding_over():
                # Pass or call
                if not self.game.round.everyone_passed():
                    legal_actions.append(PassAction())
                last_make_bid_move: MakeBidMove or None = None
                for move in reversed(self.game.round.move_sheet):
                    if isinstance(move, MakeBidMove):
                        last_make_bid_move = move
                        break
                first_bid_action_id = ActionEvent.first_bid_action_id
                next_bid_action_id = last_make_bid_move.action.action_id + 1 if last_make_bid_move else first_bid_action_id
                for bid_action_id in range(next_bid_action_id, first_bid_action_id + 27):
                    action = BidAction.from_action_id(action_id=bid_action_id)
                    legal_actions.append(action)
            elif not self.game.round.is_discarding_over():
                # Discard kitty
                hand = self.game.round.players[current_player.player_id].hand
                for card in hand:
                    action = PlayCardAction(card=card)
                    legal_actions.append(action)
            else:
                # Play card
                trick_moves = self.game.round.get_trick_moves()
                hand = self.game.round.players[current_player.player_id].hand
                legal_cards = hand
                leading = not (trick_moves and len(trick_moves) < 4)
                if not leading:

                    # Get led suit
                    led_card: FiveHundredCard = trick_moves[0].card
                    trump_suit = self.game.round.get_trump_suit()
                    led_suit = led_card.get_round_suit(trump_suit)
                    if led_suit not in self.led_suits:
                        self.led_suits.append(led_suit)
                    
                    # Get legal cards
                    cards_of_led_suit = [card for card in hand if card.get_round_suit(trump_suit) == led_suit]
                    if cards_of_led_suit:
                        legal_cards = cards_of_led_suit

                for card in legal_cards:
                    if card.rank == "RJ":
                        if leading and len(hand) != 1:
                            for suit in [suit for suit in FiveHundredCard.suits if suit not in self.led_suits]:
                                action = PlayCardAction(card=card, suit=suit)
                                legal_actions.append(action)
                        elif leading:
                            for suit in  FiveHundredCard.suits:
                                action = PlayCardAction(card=card, suit=suit)
                                legal_actions.append(action)
                        else:
                            action = PlayCardAction(card=card, suit=led_suit)
                            legal_actions.append(action)
                    else:
                        action = PlayCardAction(card=card)
                        legal_actions.append(action)
                    
        return legal_actions
