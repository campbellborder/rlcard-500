'''
    File name: five_hundred/utils/five_hundred_card.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

from rlcard.games.base import Card

class FiveHundredCard(Card):

    suits = ['S', 'C', 'D', 'H', 'RJ']
    ranks = ['4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    black_suits = ['S', 'C']
    red_suits = ['D', 'H']
    black_ranks = ['5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    red_ranks = ['4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    

    @staticmethod
    def card(card_id: int):
        return _deck[card_id]

    @staticmethod
    def get_deck() -> [Card]:
        return _deck.copy()

    def __init__(self, suit: str, rank: str):
        super().__init__(suit=suit, rank=rank)
        if self.suit == "RJ":
            self.card_id = 42
        else:
            suit_index = FiveHundredCard.suits.index(self.suit)
            rank_index = FiveHundredCard.ranks.index(self.rank)
            if self.suit in self.black_suits:
                self.card_id = 10 * suit_index + rank_index - 1
            else:
                self.card_id = 10 * suit_index + rank_index + suit_index % 2

    def get_round_suit(self, trump_suit: str or None):
        if self.suit == "RJ":
            return trump_suit
        elif trump_suit and self.is_left_bower(trump_suit):
            return trump_suit
        return self.suit

    def get_round_rank(self, trump_suit):

        if self.suit == "RJ":
            return 100
        elif trump_suit and self.is_right_bower():
            return 99
        elif trump_suit and self.is_left_bower():
            return 98
        else:
            return self.ranks.index(self.rank)

    def is_right_bower(self, trump_suit):
        return self.rank == 'J' and self.suit == trump_suit

    def is_left_bower(self, trump_suit):
        return self.rank == 'J' and self.suit == _off_trump_suits[trump_suit]

    def __str__(self):
        return f'{self.rank}{self.suit}'

    def __repr__(self):
        return f'{self.rank}{self.suit}'


# deck is always in order from 5S, 6S, ... AS, 5C, 6C, ... AC, 4D, 5D, ... AD, 4H, 5H, AH, RJ
_black_deck = [FiveHundredCard(suit=suit, rank=rank) for suit in FiveHundredCard.black_suits for rank in FiveHundredCard.black_ranks]
_red_deck = [FiveHundredCard(suit=suit, rank=rank) for suit in FiveHundredCard.red_suits for rank in FiveHundredCard.red_ranks]
_deck = _black_deck + _red_deck + [FiveHundredCard(suit='RJ', rank='')]
_off_trump_suits = {'S': 'C', 'C': 'S', 'D': 'H', 'H': 'D'}