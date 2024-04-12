"""This script contains the classes used in the Spinner game."""
import random
import numpy as np

from Board import Board
from Player import Player
from Tile import Tile
from TileSet import TileSet


class Spinner(object):
    # TODO debug chickenfeet
    def __init__(self, params):

        # Load environment parameters that will not change
        self.params = params
        self.num_players = len(params['players'])
        self.max_pips = params['max_pips']
        self.spinners = params['spinners']
        self.allow_chickenfeet = params['allow_chickenfeet']
        self.verbose = params['verbose']

        self.state_type = params['state_type']
        self.action_space_type = params['action_space_type']

        self.starting_round = self.max_pips
        self.ending_round = params['end_round']
        self.init_hand_size = params['initial_hand_size']

        # Create master set of tiles, Board, and Players
        self.tile_master = TileSet(self.max_pips, self.spinners).tiles
        self.board = Board(self, self.allow_chickenfeet)
        self.players = [Player(self, p['strategy'], p['verbose']) for p in params['players']]

        # Create parameters for specific game that can be reset for new game
        self.round = self.starting_round
        self.scores_by_round = np.zeros((self.starting_round + 1, self.num_players))

        self.current_player = random.choice(self.players)
        self.round_done = False
        self.game_done = False

        self.boneyard = self.tile_master.copy()
        self.deal()

    def reset(self):
        if self.verbose: print('Resetting....')
        self.round = self.starting_round
        self.scores_by_round = np.zeros((self.starting_round + 1, self.num_players))
        self.board.reset_for_new_round()
        for p in self.players:
            p.reset_hand()
        self.boneyard = self.tile_master.copy()
        self.deal()
        self.current_player = random.choice(self.players)
        self.play_until_need_agent_action()
        state = self.get_state()
        reward = self.get_reward()
        print('-'*60)
        print(f'Game reset. state: {state}, reward: {reward}, done: {self.game_done}')
        print('-'*60)
        return state, reward, self.game_done

    def execute_action(self, agent_action):
        if self.current_player.strategy != 'agent':
            raise Exception('Cannot execute action unless current player is agent')

        print(f'Executing action: {agent_action}')
        if self.action_space_type == 'hrl':
            action_key = {0: 'play_low', 1: 'random', 2: 'play_high'}
            agent_action = action_key[agent_action]
        self.current_player.play_turn(agent_action)
        self.update_game_and_round_done()
        self.next_player()
        self.play_until_need_agent_action()
        state = self.get_state()
        reward = self.get_reward()
        print('-'*60)
        print(f'Action {agent_action} executed.  state: {state}, reward: {reward}, done: {self.game_done}')
        print('-' * 60)
        return state, reward, self.game_done

    def play_until_need_agent_action(self):
        while not self.game_done and not self.current_player.need_agent_input():
            self.current_player.play_turn()
            self.update_game_and_round_done()
            self.next_player()
            if self.round_done and not self.game_done:
                self.setup_new_round()


    def get_state(self, state_type='two_exposed_ends'):
        if self.state_type == 'two_exposed_ends':
            exp_ends = self.board.get_usable_exposed_ends()
            match len(exp_ends):
                case 0:
                    return 110
                case 1:
                    return 100 + exp_ends[0]
                case 2:
                    return exp_ends[0] * 10 + exp_ends[1]
                case _:
                    raise Exception(f'Invalid state type, must be two exposed ends'
                                    f'exposed_ends = {exp_ends}')

        if state_type == 'vaisnorsamazingidea':
            pass

    def get_reward(self):
        if self.game_done and self.find_game_winner_index() == 0:
            return 100
        return 0

    def get_num_actions(self):
        match self.action_space_type:
            case 'hrl':
                return 3
            case _:
                raise Exception('Invalid action space type')

    def get_num_states(self):
        match self.state_type:
            case 'two_exposed_ends':
                return 111
            case _:
                raise Exception('Invalid state type')

    def calc_score_totals(self):
        return np.sum(self.scores_by_round, axis=0)

    def find_game_winner_index(self):
        return np.argmin(self.calc_score_totals())

    def is_round_done(self):
        player_hand_empty = len(self.current_player.hand) == 0
        boneyard_empty = len(self.boneyard) == 0
        if player_hand_empty:
            return True
        if boneyard_empty:
            for player in self.players:
                # Check if player has a move
                if len(player.get_valid_plays()) > 0:
                    return False
            return True
        return False

    def update_game_and_round_done(self):
        self.round_done = self.is_round_done()
        self.game_done = self.round_done and self.round == self.ending_round

    def play_game(self) -> None:
        while not self.game_done:
            self.play_round()
            if not self.game_done:
                self.setup_new_round()
        print('Game done!')
        print('Game scores by round')
        print(self.scores_by_round)
        print()
        print('Game total scores')
        print(self.calc_score_totals())

    def setup_new_round(self) -> None:
        # Figure out starting player
        prior_round_scores = self.scores_by_round[self.round, :].tolist()
        prior_round_winner_indices = [i for i, v in enumerate(prior_round_scores) if v == min(prior_round_scores)]
        self.current_player = self.players[random.choice(prior_round_winner_indices)]

        # Set round parameters
        self.round -= 1
        self.boneyard = self.tile_master.copy()
        self.board.reset_for_new_round()
        for p in self.players:
            p.reset_hand()
        self.deal()

    def play_round(self) -> None:
        """
        Method to play a round of the Spinner and update scores
        :return: None
        """
        print(f'Starting round {self.round}')
        print(self)  # printing initial game state
        self.update_game_and_round_done()

        while not self.round_done:
            self.current_player.play_turn()
            self.update_game_and_round_done()
            self.next_player()

        # update round scores
        round_scores = [p.get_score() for p in self.players]
        self.scores_by_round[self.round] = round_scores

        if self.verbose:
            print(f'Round {self.round} finished\n'
                  f'Scores for round\n'
                  f'{round_scores}\n')

    def next_player(self) -> None:
        current_player_index = self.current_player.id
        next_player_index = (current_player_index + 1) % self.num_players
        self.current_player = self.players[next_player_index]

    def draw_tile(self) -> (Tile, None):
        # Take a tile form boneyard and return it.  If boneyard empty, return None
        if self.boneyard:
            if self.verbose:
                print(f'Drawing tile from boneyard. {len(self.boneyard) - 1} tiles left.')
            return self.boneyard.pop(random.randint(0, len(self.boneyard) - 1))
        else:
            if self.verbose:
                print("Boneyard was empty when draw_tile was called.")
            return None

    def deal(self):
        if self.verbose: print(f'Dealing....')
        for player in self.players:
            player.hand = [self.draw_tile() for _ in range(self.init_hand_size)]
            player.sort_hand()
        self.update_game_and_round_done()

    def boneyard_to_str(self):
        return ' '.join(map(str, self.boneyard))

    def __str__(self):
        hands = ''
        for p in self.players:
            hands += f'Player {p.id} Hand: {p.hand_to_string()}\n'

        return (f'---Game Status---\n'
                f'Current Player: {self.current_player.id}\n'
                f'Boneyard: {self.boneyard_to_str()}\n'
                f'{self.board}'
                f'{hands}')
