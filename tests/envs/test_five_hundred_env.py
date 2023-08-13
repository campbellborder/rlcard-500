'''
    File name: test_five_hundred_env.py
    Author: Campbell Border
    Date created: 08/13/2023
'''

import unittest
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from .determism_util import is_deterministic

class TestFiveHundredEnv(unittest.TestCase):

    def test_init_and_extract_state(self):
        env = rlcard.make('five-hundred')
        state, _ = env.reset()
        # for score in state['obs']:
        #     self.assertLessEqual(score, 30)
        self.assertTrue(env is not None)

if __name__ == '__main__':
    unittest.main()
