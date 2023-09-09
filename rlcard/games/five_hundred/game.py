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
        self.num_rounds = 0

    def init_game(self):
        ''' Initialize all characters in the game and start round 1
        '''
        self.board_id = self.np_random.choice([0, 1, 2, 3])
        self.actions: List[ActionEvent] = []
        self.new_round()
        current_player_id = self.round.current_player_id
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def new_round(self):
        ''' Initialize a new round
        '''
        self.board_id = (self.board_id + 1) % 4
        self.round = FiveHundredRound(board_id=self.board_id, np_random=self.np_random)
        self.num_rounds += 1
        self.judger.reset() # Reset led cards
        
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
            ## TODO: Can't reach 500 unless you bid
            self.new_round()

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
        ''' Return whether the game is over
        '''
        team_won = self.scores[0] >= 500 or self.scores[1] >= 500
        team_lost = self.scores[0] <= -500 or self.scores[1] <= -500
        return team_won or team_lost

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

    def get_perfect_information(self):
        ''' Get state of entire game

        Return:
            state (dict): The information of the state
        '''
        state = self.round.get_perfect_information()
        state["scores"] = list(self.scores)
        return state

