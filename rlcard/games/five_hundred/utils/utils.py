'''
    File name: five_hundred/utils/utils.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

from typing import List

import numpy as np

from .five_hundred_card import FiveHundredCard


def encode_cards(cards: List[FiveHundredCard]) -> np.ndarray:  # NOTE: not used ??
    plane = np.zeros(43, dtype=int)
    for card in cards:
        plane[card.card_id] = 1
    return plane
