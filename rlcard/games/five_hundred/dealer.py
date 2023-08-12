'''
    File name: five_hundred/dealer.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

from typing import List

from .player import FiveHundredPlayer
from .utils.five_hundred_card import FiveHundredCard
from .round import FiveHundredRound


class FiveHundredDealer:
    ''' Initialize a FiveHundredDealer dealer class
    '''
    def __init__(self, np_random):
        ''' set shuffled_deck, set stock_pile
        '''
        self.np_random = np_random
        self.shuffled_deck: List[FiveHundredCard] = FiveHundredCard.get_deck()  # keep a copy of the shuffled cards at start of new hand
        self.np_random.shuffle(self.shuffled_deck)
        self.stock_pile: List[FiveHundredCard] = self.shuffled_deck.copy()

    def deal_to_player(self, player: FiveHundredPlayer, num: int):
        ''' Deal some cards from stock_pile to one player

        Args:
            player (FiveHundredPlayer): The FiveHundredPlayer object
            num (int): The number of cards to be dealt
        '''
        for _ in range(num):
            player.hand.append(self.stock_pile.pop())

    def deal_to_kitty(self, round: FiveHundredRound, num: int):
        '''
        Args:
            round (FiveHundredRound): The FiveHundredRound object
            num (int): The number of cards to be dealt
        '''
        for _ in range(num):
            round.kitty.append(self.stock_pile.pop())