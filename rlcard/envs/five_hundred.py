'''
    File name: envs/five_hundred.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

import numpy as np
from collections import OrderedDict

from rlcard.envs import Env

from rlcard.games.five_hundred import Game

from rlcard.games.five_hundred.game import FiveHundredGame
from rlcard.games.five_hundred.utils.action_event import ActionEvent
from rlcard.games.five_hundred.utils.five_hundred_card import FiveHundredCard
from rlcard.games.five_hundred.utils.move import CallMove, PlayCardMove

class FiveHundredEnv(Env):
    ''' 500 Environment
    '''
    def __init__(self, config):
        self.name = 'five_hundred'
        self.game = Game()
        super().__init__(config=config)
        self.fiveHundredPayoffDelegate = DefaultFiveHundredPayoffDelegate()
        self.fiveHundredStateExtractor = DefaultFiveHundredStateExtractor()
        state_shape_size = self.fiveHundredStateExtractor.get_state_shape_size()
        self.state_shape = [[1, state_shape_size] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def get_payoffs(self):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        return self.fiveHundredPayoffDelegate.get_payoffs(game=self.game)

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        return self.game.round.get_perfect_information()

    def _extract_state(self, state):
        ''' Extract useful information from state for RL.

        Args:
            state (dict): The raw state

        Returns:
            (numpy.array): The extracted state
        '''
        return self.fiveHundredStateExtractor.extract_state(game=self.game)

    def _decode_action(self, action_id):
        ''' Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (ActionEvent): The action that will be passed to the game engine.
        '''
        return ActionEvent.from_action_id(action_id=action_id)

    def _get_legal_actions(self):
        ''' Get all legal actions for current state.

        Returns:
            (list): A list of legal actions' id.
        '''

        return self.game.judger.get_legal_actions()


class FiveHundredPayoffDelegate(object):

    def get_payoffs(self, game: FiveHundredGame):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            (list): A list of payoffs for each player.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError


class DefaultFiveHundredPayoffDelegate(FiveHundredPayoffDelegate):

    def __init__(self):
        self.make_bid_bonus = 2

    def get_payoffs(self, game: FiveHundredGame):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        contract_bid_move = game.round.contract_bid_move
        if contract_bid_move:
            declarer = contract_bid_move.player
            bid_trick_count = contract_bid_move.action.bid_amount + 6
            won_trick_counts = game.round.won_trick_counts
            declarer_won_trick_count = won_trick_counts[declarer.player_id % 2]
            defender_won_trick_count = won_trick_counts[(declarer.player_id + 1) % 2]
            declarer_payoff = bid_trick_count + self.make_bid_bonus if bid_trick_count <= declarer_won_trick_count else declarer_won_trick_count - bid_trick_count
            defender_payoff = defender_won_trick_count
            payoffs = []
            for player_id in range(4):
                payoff = declarer_payoff if player_id % 2 == declarer.player_id % 2 else defender_payoff
                payoffs.append(payoff)
        else:
            payoffs = [0, 0, 0, 0]
        return np.array(payoffs)


class FiveHundredStateExtractor(object):  # interface

    def get_state_shape_size(self) -> int:
        raise NotImplementedError

    def extract_state(self, game: FiveHundredGame):
        ''' Extract useful information from state for RL. Must be implemented in the child class.

        Args:
            game (FiveHundredGame): The game

        Returns:
            (numpy.array): The extracted state
        '''
        raise NotImplementedError

    @staticmethod
    def get_legal_actions(game: FiveHundredGame):
        ''' Get all legal actions for current state.

        Returns:
            (OrderedDict): A OrderedDict of legal actions' id.
        '''
        legal_actions = game.judger.get_legal_actions()
        legal_actions_ids = {action_event.action_id: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)


class DefaultFiveHundredStateExtractor(FiveHundredStateExtractor):

    # Score:            2 [our_score, their_score]
    # Game phase:       3 [bidding, discarding, playing]
    # Hand:             43 [4S, 4C, 5S, ..., AD, AH, JK] (one hot)
    # Bid(s):           27 [6S, 6C, ..., 8S, M, 8C, ... 10H, 10NT, OM] (one hot)
    # Player position:  4 [0, 1, 2, 3] (one hot)
    # Passed players:   4 [0, 1, 2, 3] (one hot)
    # Tricks:           10 [1, 2, ..., 10] (one hot)
    # Trick cards:      43 [4S, 4C, 5S, ..., AD, AH, JK] (1, 2, 3 in order)
    # Opponent's hand   43              '                (if open misere)
    # TOTAL:            136

    def __init__(self):
        super().__init__()

        self.phase_indices = {"bid": 2, "discard": 3, "play": 4}

    def get_state_shape_size(self) -> int:
        return 179

    def extract_state(self, game: FiveHundredGame):
        ''' Extract useful information from state for RL.

        Args:
            game (FiveHundredGame): The game

        Returns:
            (numpy.array): The extracted state
        '''
        state = np.zeros(self.get_state_shape_size())
        info = game.get_perfect_information()
        current_player_id = info['current_player_id']

        # Our score, their score (0 - 1)
        scores = info['scores']
        state[0] = scores[current_player_id % 2]
        state[1] = scores[1 - (current_player_id % 2)]

        # Game phase (2 - 4)
        phase = info['round_phase']
        state[self.phase_indices[phase]] = 1

        # Hand (5 - 47)
        hand = info['hands'][current_player_id]
        for card in hand:
            state[card.card_id + 5] = 1
        
        # Bid(s) (48 - 74)
        bids = info['bids']
        all_bids = [bid for player_bids in bids for bid in player_bids]
        all_bids.sort(key=lambda x: x.action.action_id)
        if phase == "bid":
            for bid in all_bids:
                if bid.action.action_id > 1: # ignore no bid and pass
                    state[bid.action.action_id + 46] = 1 # action_id 2 corresponds to 48
        else: 
            for bid in all_bids[::-1]:
                if bid.action.action_id > 1: # ignore no bid and pass
                    state[bid.action.action_id + 46] = 1
                    break # only the winning bid

        # Player position (75 - 78)
        lead = info['lead']
        state[75 + ((current_player_id - lead) % 4)] = 1

        # Passed players (79 - 82)
        if info['round_phase'] == 'bid':
            passed = info['players_passed']
            state[79:83] =  passed[lead:] + passed[:lead]

        # Tricks (83 - 92)
        tricks_won = info["tricks_won"]
        for i in range(10):
            if tricks_won[i] == current_player_id % 2:
                state[83 + i] = 1

        # Trick cards (93 - 135)
        trick_cards = info['trick_cards']
        for i, card in enumerate(trick_cards):
            if card:
                print(current_player_id)
                print(lead)
                state[93 + card.card_id] = ((i - lead) % 4) + 1

        # Opponent's hand (136 - 178)
        open_misere_lead = info['open_misere_lead']
        if open_misere_lead != -1:
            hand = info['hands'][open_misere_lead]
            for card in hand:
                state[card.card_id + 5] = 1

        return state
