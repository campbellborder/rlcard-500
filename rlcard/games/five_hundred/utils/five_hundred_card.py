'''
    File name: five_hundred/utils/five_hundred_card.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

from rlcard.games.base import Card


class FiveHundredCard(Card):

    suits = ['C', 'D', 'H', 'S']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    @staticmethod
    def card(card_id: int):
        return _deck[card_id]

    @staticmethod
    def get_deck() -> [Card]:
        return _deck.copy()

    def __init__(self, suit: str, rank: str):
        super().__init__(suit=suit, rank=rank)
        suit_index = FiveHundredCard.suits.index(self.suit)
        rank_index = FiveHundredCard.ranks.index(self.rank)
        self.card_id = 13 * suit_index + rank_index

    def __str__(self):
        return f'{self.rank}{self.suit}'

    def __repr__(self):
        return f'{self.rank}{self.suit}'


# deck is always in order from 2C, ... KC, AC, 2D, ... KD, AD, 2H, ... KH, AH, 2S, ... KS, AS
_deck = [FiveHundredCard(suit=suit, rank=rank) for suit in FiveHundredCard.suits for rank in FiveHundredCard.ranks]  # want this to be read-only
