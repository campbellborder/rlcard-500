'''
    File name: five_hundred/game.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

from typing import List

import numpy as np

from .judger import FiveHundredJudger
from .round import FiveHundredRound
from .utils.action_event import ActionEvent, CallActionEvent, PlayCardAction


class FiveHundredGame:
    ''' Game class. This class will interact with outer environment.
    '''

    def __init__(self, allow_step_back=False):
        '''Initialize the class FiveHundredGame
        '''
        self.allow_step_back: bool = allow_step_back
        self.np_random = np.random.RandomState()
        self.judger: FiveHundredJudger = FiveHundredJudger(game=self)
        self.actions: [ActionEvent] = []  # must reset in init_game
        self.round: FiveHundredRound or None = None  # must reset in init_game
        self.num_players: int = 4
        self.scores: (int, int) = (0, 0) # (N-S, E-W)

    def init_game(self):
        ''' Initialize all characters in the game and start round 1
        '''
        self.board_id = self.np_random.choice([0, 1, 2, 3])
        self.actions: List[ActionEvent] = []
        self.init_round()
        current_player_id = self.round.current_player_id
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def init_round(self):
        ''' Initialize a new round
        '''
        self.board_id = (self.board_id + 1) % 4
        self.round = FiveHundredRound(board_id=self.board_id, np_random=self.np_random)
        

    def step(self, action: ActionEvent):
        ''' Perform game action and return next player number, and the state for next player
        '''
        if isinstance(action, CallActionEvent):
            self.round.make_call(action=action)
        elif isinstance(action, PlayCardAction):
            self.round.play_card(action=action)
        else:
            raise Exception(f'Unknown step action={action}')
        self.actions.append(action)

        # If round is over, start a new round
        if self.round.is_over():
            round_points = self.round.get_points()
            self.scores = tuple(sum(x) for x in zip(self.scores, round_points))
            self.board_id = (self.board_id + 1) % 4
            self.round = FiveHundredRound(board_id=self.board_id, np_random=self.np_random)

        # Get next player and state
        next_player_id = self.round.current_player_id
        next_state = self.get_state(player_id=next_player_id)
        return next_state, next_player_id

    def get_num_players(self) -> int:
        ''' Return the number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_num_actions() -> int:
        ''' Return the number of possible actions in the game
        '''
        return ActionEvent.get_num_actions()

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        return self.round.current_player_id

    def is_over(self) -> bool:
        ''' Return whether the current round is over
        '''
        return self.round.is_over()

    def get_state(self, player_id: int):  # wch: not really used
        ''' Get player's state

        Return:
            state (dict): The information of the state
        '''
        state = {}
        state['player_id'] = player_id
        state['current_player_id'] = self.round.current_player_id
        state['hand'] = self.round.players[player_id].hand
        return state
