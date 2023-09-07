'''
    File name: five_hundred/utils/action_event.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

from .five_hundred_card import FiveHundredCard

## NOTE: might need to put misere inbetween 8S and 8C

# ====================================
# Action_ids:
#       0 -> no_bid_action_id
#       1 -> pass_action_id
#       2 to 12 -> bid_action_id (6S to 8S)
#       13 -> misere_action_id
#       14 to 27 -> bid_action_id (8C to 10NT)
#       28 -> open_misere_action_id
#       29 to 70 -> play_card_action_id (normal cards)
#       71 to 74 -> play_card_action_id (joker, as spade, club, diamond, heart)
# ====================================


class ActionEvent(object):  # Interface

    no_bid_action_id = 0
    pass_action_id = 1
    first_bid_action_id = 2
    last_bid_action_id = 27
    misere_bid_action_id = 13
    open_misere_bid_action_id = 28
    first_play_card_action_id = 29
    last_play_card_action_id = 70
    first_play_joker_action_id = 71
    last_play_joker_action_id = 74

    def __init__(self, action_id: int):
        self.action_id = action_id

    def __eq__(self, other):
        result = False
        if isinstance(other, ActionEvent):
            result = self.action_id == other.action_id
        return result

    @staticmethod
    def from_action_id(action_id: int):
        if action_id == ActionEvent.pass_action_id:
            return PassAction()
        elif action_id == ActionEvent.misere_bid_action_id:
            return BidAction(None, None, misere=True)
        elif action_id == ActionEvent.open_misere_bid_action_id:
            return BidAction(None, None, misere=True, open=True)
        elif ActionEvent.first_bid_action_id <= action_id <= ActionEvent.last_bid_action_id:
            if action_id < ActionEvent.misere_bid_action_id:
                bid_amount = (action_id - ActionEvent.first_bid_action_id) // 5 + 6
                bid_suit_id = (action_id - ActionEvent.first_bid_action_id) % 5
            else:
                bid_amount = (action_id - ActionEvent.first_bid_action_id - 1) // 5 + 6
                bid_suit_id = (action_id - ActionEvent.first_bid_action_id - 1) % 5
            bid_suit = FiveHundredCard.suits[bid_suit_id] if bid_suit_id < 4 else None
            return BidAction(bid_amount, bid_suit)
        elif ActionEvent.first_play_joker_action_id <= action_id <= ActionEvent.last_play_joker_action_id:
            suit_id = action_id - ActionEvent.first_play_joker_action_id
            suit = FiveHundredCard.suits[suit_id]
            card_id = ActionEvent.first_play_joker_action_id - ActionEvent.first_play_card_action_id
            card = FiveHundredCard.card(card_id=card_id)
            card.suit = suit
            return PlayCardAction(card=card)
        elif ActionEvent.first_play_card_action_id <= action_id <= ActionEvent.last_play_card_action_id:
            card_id = action_id - ActionEvent.first_play_card_action_id
            card = FiveHundredCard.card(card_id=card_id)
            return PlayCardAction(card=card)
        else:
            raise Exception(f'ActionEvent from_action_id: invalid action_id={action_id}')

    @staticmethod
    def get_num_actions():
        ''' Return the number of possible actions in the game
        '''
        return 1 + 1 + 27 + 46  # no_bid, pass, 27 bids, 46 play_cards


class CallActionEvent(ActionEvent):  # Interface
    pass


class PassAction(CallActionEvent):

    def __init__(self):
        super().__init__(action_id=ActionEvent.pass_action_id)

    def __str__(self):
        return "P"

    def __repr__(self):
        return "P"


class BidAction(CallActionEvent):

    ## TODO: Calculate this
    bid_points = {"N": 0, "P": 0,
                "6S": 40,            "6C": 60, "6D": 80, "6H": 100, "6NT": 120,
                "7S": 140,           "7C": 160, "7D": 180, "7H": 200, "7NT": 220,
                "8S": 240, "M": 250, "8C": 260, "8D": 280, "8H": 300, "8NT": 320,
                "9S": 340,           "9C": 360, "9D": 380, "9H": 400, "9NT": 420,
                "10S": 440,          "10C": 460, "10D": 480, "10H": 500, "10NT": 520, "OM": 500}

    def __init__(self, bid_amount: int or None, bid_suit: str or None, misere=False, open=False):
        
        # Get bid suit id
        suits = FiveHundredCard.suits + ["NT"]
        if bid_suit and bid_suit not in suits:
            raise Exception(f'BidAction has invalid suit: {bid_suit}')
        elif bid_suit in suits:
            bid_suit_id = suits.index(bid_suit)
        elif bid_amount:
            bid_suit_id = 4

        # Get action id
        if misere:
            bid_action_id = 28 if open else 13
            bid_amount = 10
        else:
            bid_action_id = bid_suit_id + 5 * (bid_amount - 6) + ActionEvent.first_bid_action_id
            if bid_action_id >= ActionEvent.misere_bid_action_id: bid_action_id += 1
        super().__init__(action_id=bid_action_id)
        
        self.bid_amount = bid_amount
        self.bid_suit = bid_suit
        self.misere = misere
        self.open = open
        self.bid_points = BidAction.bid_points[self.__str__()]

    def __str__(self):
        if self.misere:
            return 'OM' if self.open else 'M'
        bid_suit = self.bid_suit
        if not bid_suit:
            bid_suit = 'NT'
        return f'{self.bid_amount}{bid_suit}'

    def __repr__(self):
        return self.__str__()


class PlayCardAction(ActionEvent):

    def __init__(self, card: FiveHundredCard):
        play_card_action_id = ActionEvent.first_play_card_action_id + card.card_id
        super().__init__(action_id=play_card_action_id)
        self.card: FiveHundredCard = card

    def __str__(self):
        return f"{self.card}"

    def __repr__(self):
        return f"{self.card}"