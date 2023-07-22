import unittest
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from .determism_util import is_deterministic

class TestFiveHundredEnv(unittest.TestCase):

    def test_init_and_extract_state(self):
        env = rlcard.make('five_hundred')
        state, _ = env.reset()
        # for score in state['obs']:
        #     self.assertLessEqual(score, 30)
        self.assertTrue(env is not None)

if __name__ == '__main__':
    unittest.main()
