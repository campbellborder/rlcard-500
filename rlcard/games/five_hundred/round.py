'''
    File name: five_hundred/round.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

from typing import List

from .dealer import FiveHundredDealer
from .player import FiveHundredPlayer

from .utils.action_event import CallActionEvent, PassAction, BidAction, PlayCardAction
from .utils.move import FiveHundredMove, DealHandMove, PlayCardMove, MakeBidMove, MakePassMove, CallMove
from .utils.tray import Tray
from .utils.five_hundred_card import FiveHundredCard


class FiveHundredRound:

    @property
    def dealer_id(self) -> int:
        return self.tray.dealer_id

    @property
    def board_id(self) -> int:
        return self.tray.board_id

    @property
    def round_phase(self):
        if self.is_over():
            result = 'over'
        elif not self.is_bidding_over():
            result = 'bid'
        elif not self.is_discarding_over():
            result = 'discard'
        else:
            result = 'play'
        return result

    def __init__(self, board_id: int, np_random):
        ''' Initialize the round class

            The round class maintains the following instances:
                1) dealer: the dealer of the round; dealer has trick_pile
                2) players: the players in the round; each player has his own hand_pile
                3) current_player_id: the id of the current player who has the move
                4) kitty: the cards in the kitty
                5) play_card_count: count of PlayCardMoves
                6) move_sheet: history of the moves of the players (including the deal_hand_move)

        Args:
            num_players: int
            board_id: int
            np_random
        '''
        tray = Tray(board_id=board_id)
        self.num_players = 4
        self.tray = tray
        self.np_random = np_random

        self.dealer: FiveHundredDealer = FiveHundredDealer(self.np_random)
        self.kitty: [FiveHundredCard] = []

        self.players: List[FiveHundredPlayer] = []
        for player_id in range(self.num_players):
            self.players.append(FiveHundredPlayer(player_id=player_id, np_random=self.np_random))
        self.players_passed = [0] * self.num_players
        
        self.contract_bid_move: MakeBidMove or None = None
        self.play_card_count: int = 0
        self.won_trick_counts = [0] * 4 # count of tricks won by each player
        self.won_tricks = [-1] * 10
        self.move_sheet: List[FiveHundredMove] = []
        self.move_sheet.append(DealHandMove(dealer=self.players[self.dealer_id], shuffled_deck=self.dealer.shuffled_deck))
        self.current_player_id: int = (self.dealer_id + 1) % 4

        # Deal cards
        for num_cards in [3, 4, 3]:
            for player_id in range(self.num_players):
                player = self.players[player_id]
                self.dealer.deal_cards(hand=player.hand, num=num_cards)
            self.dealer.deal_cards(hand=self.kitty, num=1)

    def is_bidding_over(self) -> bool:
        ''' Return whether the current bidding is over
        '''
        return sum(self.players_passed) == 3 and len(self.move_sheet) > 4 # Because of deal hand move

    def everyone_passed(self) -> bool:
        ''' Return whether 3 players have passed
        '''
        return sum(self.players_passed) == 3
    
    def is_discarding_over(self) -> bool:
        ''' Return whether the declarer has discarded the kitty
        '''
        is_discarding_over = False
        if self.is_bidding_over():
            if len(self.get_declarer().hand) <= 10:
                is_discarding_over = True
        return is_discarding_over

    def is_over(self) -> bool:
        ''' Return whether the current game is over
        '''
        return sum(self.won_trick_counts) == 10

    def get_current_player(self) -> FiveHundredPlayer or None:
        ''' Return the current player
        '''
        current_player_id = self.current_player_id
        return self.players[current_player_id] if current_player_id is not None else None

    def get_trick_moves(self) -> List[PlayCardMove]:
        ''' Return a list of the PlayCardMoves associated with the current trick
        '''
        trick_moves: List[PlayCardMove] = []
        if self.is_bidding_over() and self.is_discarding_over():
            full_trick_count = self.get_full_trick_count()
            if self.play_card_count > 0:
                trick_pile_count = self.play_card_count % full_trick_count
                if trick_pile_count == 0:
                    trick_pile_count = full_trick_count
                trick_moves = self.move_sheet[-trick_pile_count:]

                # TODO: do we need this anymore?
                if len(trick_moves) != trick_pile_count:
                    raise Exception(f'get_trick_moves: count of trick_moves={[str(move.card) for move in trick_moves]} does not equal {trick_pile_count}')
        return trick_moves

    def get_full_trick_count(self):

        if self.is_bidding_over():
            return 4 if not self.contract_bid_move.action.misere else 3

    def get_trump_suit(self) -> str or None:
        ''' Gets the suit of the winning bid
        '''
        trump_suit = None
        if self.is_bidding_over() and self.contract_bid_move:
            bid_suit = self.contract_bid_move.action.bid_suit
            trump_suit = bid_suit if bid_suit != "NT" else None
        return trump_suit
    
    def distribute_kitty(self):
        ''' Distribute the kitty to the declarer
        '''
        self.get_declarer().hand += self.kitty
        self.kitty = []

    def make_call(self, action: CallActionEvent):
        # when current_player takes CallActionEvent step, the move is recorded and executed
        # TODO: If bidding is over, error
        current_player = self.players[self.current_player_id]
        if isinstance(action, PassAction):
            if sum(self.players_passed) == 3:
                raise Exception("Can't pass - three players have already passed")
            self.move_sheet.append(MakePassMove(current_player))
            self.players_passed[self.current_player_id] = 1
        elif isinstance(action, BidAction):
            make_bid_move = MakeBidMove(current_player, action)
            self.contract_bid_move = make_bid_move
            self.move_sheet.append(make_bid_move)
        
        if self.is_bidding_over(): # Distribute kitty to declarer
            self.distribute_kitty()
        self.next_player()

    def play_card(self, action: PlayCardAction):
        # when current_player takes PlayCardAction step, the move is recorded and executed
        # TODO: if still bidding, error
        # TODO: check if valid move?
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(PlayCardMove(current_player, action))
        
        # Discarding kitty
        if not self.is_discarding_over():
            current_player.remove_card_from_hand(action.card)
            self.kitty.append(action.card)
        else:
            # Playing a card
            self.play_card_count += 1
            current_player.remove_card_from_hand(action.card)
            if len(self.get_trick_moves()) == self.get_full_trick_count():
                trick_winner = self.get_trick_winner()
                self.current_player_id = trick_winner.player_id
                self.won_tricks[sum(self.won_trick_counts)] = trick_winner.player_id % 2
                self.won_trick_counts[trick_winner.player_id] += 1
            else:
                self.next_player()

    def get_trick_winner(self):
        trick_moves = self.get_trick_moves()
        trump_suit = self.get_trump_suit()

        winning_move = trick_moves[0]
        for move in trick_moves[1:]:
            if move.card.get_round_suit(trump_suit) == winning_move.card.get_round_suit(trump_suit):
                if move.card.get_round_rank(trump_suit) > winning_move.card.get_round_rank(trump_suit):
                    winning_move = move
            elif move.card.get_round_suit(trump_suit) == trump_suit:
                winning_move = move

        return winning_move.player

    def next_player(self):
        
        if not self.is_over():
            if self.is_bidding_over():
                if not self.is_discarding_over():
                    self.current_player_id = self.contract_bid_move.player.player_id
                else: # Next player in rotation (unless misere)
                    misere = self.contract_bid_move.action.misere
                    if misere and self.current_player_id == (self.contract_bid_move.player.player_id + 1) % 4:
                        self.current_player_id = (self.current_player_id + 2) % 4
                    else:
                        self.current_player_id = (self.current_player_id + 1) % 4
            else:
                # Next non-passed player
                while True:
                    self.current_player_id = (self.current_player_id + 1) % 4
                    if not self.players_passed[self.current_player_id]: break

    def get_declarer(self) -> FiveHundredPlayer or None:
        declarer = None
        if self.contract_bid_move:
            declarer = self.contract_bid_move.player
        return declarer
    
    def get_points(self) -> (int, int):
        points = [0, 0]
        if self.is_over():
            bid_points = self.contract_bid_move.action.bid_points
            declarer_id = self.get_declarer().player_id
            if self.bid_achieved():
                points[declarer_id % 2] += bid_points
            else:
                points[declarer_id % 2] -= bid_points
            if not self.contract_bid_move.action.misere:
                opponent_tricks = self.won_trick_counts[(declarer_id + 1) % 4] + self.won_trick_counts[(declarer_id + 3) % 4]
                points[(declarer_id + 1) % 2] += opponent_tricks * 10
        return points

    def bid_achieved(self):
        declarer_id = self.get_declarer().player_id
        declarer_partner = (declarer_id + 2) % 4
        tricks_won = self.won_trick_counts[declarer_id] + self.won_trick_counts[declarer_partner]
        if self.contract_bid_move.action.misere:
            return tricks_won == 0
        return tricks_won >= self.contract_bid_move.action.bid_amount

    def get_perfect_information(self):
        
        state = {}

        # Get each players bids
        bids = [[], [], [], []]
        for move in self.move_sheet:
            if isinstance(move, CallMove):
                bids[move.player.player_id].append(move)
        
        # Get current trick moves
        lead = (self.dealer_id + 1) % 4 # Defaults to the player left of the dealer
        ordered_trick_cards = [None, None, None, None]
        if self.is_bidding_over() and self.is_discarding_over():
            trick_moves = self.get_trick_moves()
            for trick_move in trick_moves:
                if trick_move.card.rank == "RJ": # Because there are multiple RJ cards
                    ordered_trick_cards[trick_move.player.player_id] = FiveHundredCard.card(42)
                else:
                  ordered_trick_cards[trick_move.player.player_id] = trick_move.card
            if len(trick_moves):
                lead = trick_moves[0].player.player_id
            else:
                lead = self.current_player_id
        
        state['move_count'] = len(self.move_sheet)
        state['tray'] = self.tray
        state['current_player_id'] = self.current_player_id
        state['round_phase'] = self.round_phase
        state['bids'] = bids
        state['contract'] = self.contract_bid_move if self.is_bidding_over() and self.contract_bid_move else None
        state['hands'] = [player.hand for player in self.players]
        state['kitty'] = self.kitty
        state['trick_cards'] = ordered_trick_cards
        state['lead'] = lead
        state['tricks_won'] = self.won_tricks
        state['tricks_won_counts'] = self.won_trick_counts
        state['players_passed'] = self.players_passed
        state['open_misere_lead'] = self.get_declarer().player_id \
                if self.contract_bid_move and self.contract_bid_move.action.action_id == 28 \
                and sum(self.won_trick_counts) > 0 else -1
        return state
