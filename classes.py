"""This script contains the classes used in the Spinner game."""
import random
from itertools import combinations_with_replacement

import numpy as np


class Tile:
    """
    Represents a single tile in the game of Spinner.
    Attributes:
        low, high: the value of each end of the tile.  These are always ordered from low to high except for doubles
                    'S' is for spinner and is always the high end.
        is_spinner: True if the tile has a spinner
        is_double: True if the tile has a double
        value: the value of the tile
        spinner_value: the value of a spinner end for points
    """

    num_tiles = 0

    def __init__(self, low, high):
        self.id = Tile.num_tiles
        Tile.num_tiles += 1
        self.low = low
        self.high = high
        self.is_spinner = 'S' in [self.low, self.high]
        self.is_double = self.high == self.low
        self.value = 0
        self.spinner_value = 10

        # Ensure low is low and high is high
        if self.is_spinner:
            if self.low == 'S' and not self.is_double:
                self.low, self.high = self.high, self.low
        else:
            if self.low > self.high:
                self.low, self.high = self.high, self.low

        # Set value
        if self.is_spinner:
            if self.is_double:
                self.value = 2 * self.spinner_value
            else:
                self.value = self.low + self.spinner_value
        else:
            self.value = self.low + self.high

    def __eq__(self, other):
        return self.low == other.low and self.high == other.high

    def __str__(self):
        return str(self.low) + '|' + str(self.high)


class TileSet:
    """
    Represents a full set of tiles for the game of Spinner

    Attributes:
        tiles: the full set of tiles in the game

    Methods:
        shuffle(): shuffles the tiles in place
    """

    def __init__(self, max_pips=9, spinners=True):
        ends = list(range(max_pips + 1))
        if spinners:
            ends.append('S')
        self.tiles = [Tile(low, high) for low, high in combinations_with_replacement(ends, 2)]

    def shuffle(self):
        random.shuffle(self.tiles)

    def __str__(self):
        return ' '.join(map(str, self.tiles))


class Player:
    """
    Represents a player in the game.  Game be an AI, human, or agent depending on strategy
    Attributes:
        game (Game): the game
        strategy (str): the strategy deployed by the player.  Can be 'random', 'play_high', 'play_low',
                        'human' or 'agent'
        hand (Hand): the hand of the player, list of Tile objects
        verbose: flag for output
        id:  the player id
        max_turns: limit on maximum turns for a player for debugging.  Set to None for no limit.
    """
    id = 0

    def __init__(self, game, strategy, verbose=False, max_turns=None):
        self.game = game
        self.strategy = strategy
        self.hand = []
        self.verbose = verbose
        self.id = Player.id
        self.max_turns = max_turns
        Player.id += 1
        self.actions = [0, 1, 2]  # 0 = random, 1 = play low, 2 = play high

    def reset_hand(self):
        self.hand = []

    def play_turn(self):
        
        # get available actions
        available_actions = self.get_available_actions()
        if self.verbose:
            print(f'\nPlayer {self.id} turn - Round: {self.game.round}\n'
                  f'Boneyard: {self.game.boneyard_to_str()}\n'
                  f'{self.game.board}'
                  f'Hand: {self.hand_to_string()}\n'
                  f'Available Actions (Hand Index, Tile Value): {available_actions}')

        # choose an action if possible or draw a tile
        if available_actions:
            action = self.choose_action(available_actions)
            self.place_tile_from_hand(action)
            if self.verbose:
                print(f'Player action {action}\n'
                      f'New Hand {self.hand_to_string()}\n')
        else:
            self.draw_tile_to_hand()
            if self.verbose:
                print(f'Player action: Draw\n'
                      f'New Hand: {self.hand_to_string()}\n')

    def get_available_actions(self):
        """
        Method to search players hand for playable tiles given the playable exposed ends of the board
        :return: List of actions that are possible given a player's hand and the board's exposed tiles
                    Actions are tuples containing the index of a playable tile in the players hand
                    and the value of the end of the tile to be played'
        """
        available_actions = []
        if len(self.game.board.tiles) == 0:             # for empty board, find r|r or S|S
            r = self.game.round
            for index, tile in enumerate(self.hand):
                if tile.is_double and tile.high in [r, 'S']:
                    available_actions.append((index, r))
        else:                                           # after initial tile played
            usable_exposed = self.game.board.get_usable_exposed_ends()
            for index, tile in enumerate(self.hand):
                if tile.low in usable_exposed:
                    available_actions.append((index, tile.low))
                if tile.high in usable_exposed:
                    if not tile.is_double:
                        available_actions.append((index, tile.high))
                if tile.high == 'S':
                    for e in usable_exposed:
                        available_actions.append((index, e))
        return available_actions

    def draw_tile_to_hand(self):
        """
        This method removes a tile from the boneyard, puts it in the players hand and sort the
        players hand by tile index.  If the boneyard is empty, prints a message to the console
        :return: None
        """
        new_tile = self.game.draw_tile()
        if new_tile:
            self.hand.append(new_tile)
            self.sort_hand()
        else:
            print('Boneyard empty!!!!!!!!!!')

    def place_tile_from_hand(self, action):
        """
        This method removes a tile from the players hand and sends it to the board with the end to play on
        using  the receive_tile method for the board.
        :param action: tuple specifiy the index of the tile to play form the players hand and the exposed end
        oof the board on which the tile should be placed.
        :return: None
        """
        if len(self.hand) == 0:
            raise Exception(f'Player hand is empty, cannot place_tile_from_hand')
        tile_to_play = self.hand.pop(action[0])
        value_of_end_to_play = action[1]
        self.game.board.receive_tile(tile_to_play, value_of_end_to_play)

    def choose_action(self, action_list):
        """
        """

        # action list is a tuple of (left tile value, right tile value)

        # if only one option avaalable, return it
        if len(action_list) == 1:
            return action_list[0]
        

        

    def get_score(self):
        values = [t.value for t in self.hand]
        return sum(values)

    def sort_hand(self):
        self.hand.sort(key=lambda t: t.id)

    def hand_to_string(self):
        return ' '.join(map(str, self.hand)) if self.hand else 'Empty'

    def __str__(self):
        return f'Player {self.id} Hand {self.hand_to_string()}'


class Board:
    def __init__(self, game, allow_chickenfeet=False):
        self.game = game
        self.tiles = []
        self.exposed_ends = []
        self.exposed_double = None
        self.exposed_double_count = 0
        self.allow_chickenfeet = allow_chickenfeet
        self.tiles_per_double = 3 if allow_chickenfeet else 1

    def reset_for_new_round(self):
        self.tiles = []
        self.exposed_ends = []
        self.exposed_double = None
        self.exposed_double_count = 0

    def receive_tile(self, tile, end_value):
        # TODO needs to account for spinners
        # TODO discuss if we need to account for tile played with spinner exposed, this is legal but unwise
        # TODO discuss action space for playing spinner, needs to also include which end spinner is being played

        if len(self.tiles) == 0:
            r = self.game.round
            if (tile.low, tile.high) not in [(r, r), ('S', 'S')]:
                raise Exception(f'Receive tile error, first tile must be {r}|{r} or S|S, not {tile}')
            self.tiles.append(tile)
            self.exposed_ends = [r, r]

        elif len(self.tiles) in [1, 2]:
            r = self.game.round
            if tile.low not in [r, 'S'] and tile.high not in [r, 'S']:
                raise Exception(f'Receive tile error, round {r} tile {len(self.tiles)} must have {r} or S end, passed tile is {tile}')
            self.add_tile_adjust_exposed_ends(tile, end_value)
            if len(self.tiles) == 3 and self.allow_chickenfeet:
                self.exposed_ends += [r, r]

        else:  # fourth tile or later
            if self.exposed_double:
                if self.exposed_double_count <= self.tiles_per_double:
                    self.exposed_double_count += 1
                    if self.exposed_double_count==self.tiles_per_double:
                        self.exposed_double = None
                        self.exposed_double_count = 0
                    self.add_tile_adjust_exposed_ends(tile, end_value)

            elif tile.is_double:
                self.exposed_double = end_value     # end_value works for double spinner or double number
                self.exposed_double_count = 0
                self.tiles.append(tile)

            else:
                if end_value not in self.exposed_ends:
                    raise Exception(f'Board.receive_tile error.'
                                    f'Cannot add tile to board if exposed end {end_value} not '
                                    f'in exposed_ends {self.exposed_ends}')
                self.add_tile_adjust_exposed_ends(tile, end_value)

    def add_tile_adjust_exposed_ends(self, tile, end_value) -> None:
        self.tiles.append(tile)
        if tile.is_double:
            raise Exception(f'Board.receive_tile error. add_tile_adjust_exposed_ends cannot receive double.  tile={tile}')
        elif tile.is_spinner:
            self.exposed_ends.remove(end_value)
            self.exposed_ends.append(tile.low)
        else:
            if end_value == tile.low:
                self.exposed_ends.remove(tile.low)
                self.exposed_ends.append(tile.high)
            else:
                self.exposed_ends.remove(tile.high)
                self.exposed_ends.append(tile.low)

    def get_usable_exposed_ends(self) -> list:
        if self.exposed_double:
            return [self.exposed_double]
        if len(self.tiles) == 0:
            return []
        if len(self.tiles) in [1,2]:
            return [self.game.round]
        else:
            return sorted(list(set(self.exposed_ends)))

    def __str__(self):
        return (f'Board Tiles: {" ".join(map(str, self.tiles))}\n'
                f'Exposed ends: {self.exposed_ends}\n')


class Game(object):
    def __init__(self, params):
        self.params = params
        self.num_players = len(params['players'])
        self.max_pips = params['max_pips']
        self.spinners = params['spinners']
        self.allow_chickenfeet = params['allow_chickenfeet']

        self.tile_master = TileSet(self.max_pips, self.spinners).tiles
        self.boneyard = self.tile_master.copy()
        self.board = Board(self, self.allow_chickenfeet)
        self.players = [Player(self, p['strategy'], p['verbose']) for p in params['players']]
        self.init_hand_size = params['initial_hand_size']

        self.max_round = self.max_pips  # start at round 9 and count down
        self.round = self.max_round
        self.min_round = params['end_round']
        self.rounds_to_play = self.max_round - self.min_round + 1
        self.scores_by_round = np.zeros((self.max_round + 1, self.num_players))
        self.total_scores = np.zeros((1, self.num_players))

        self.current_player = self.players[random.randint(0, self.num_players - 1)]

    def reset(self):
        pass

    def execute_action(self, action) -> tuple[list, int, bool]:
        return (new_state, reward, done)

    def get_state(self, state_type='basic'):
        pass

    def get_number_of_states(self) -> int:
        pass

    def get_number_of_actions(self) -> int:
        pass

    def play_game(self, verbose=False) -> None:
        for self.round in range(self.max_round, self.min_round - 1, -1):
            round_scores = self.play_round(verbose=verbose)
            next_player_index = random.choice(
                [i for i, v in enumerate(round_scores) if v == max(round_scores)])
            self.scores_by_round[self.round] = round_scores
            self.current_player = self.players[next_player_index]
        self.total_scores = np.sum(self.scores_by_round, axis=0)

    def reset_for_new_round(self) -> None:
        self.boneyard = self.tile_master.copy()
        self.board.reset_for_new_round()
        for p in self.players:
            p.reset_hand()

    def play_round(self, verbose=False) -> list:
        """
        Method to play a round of the Spinner
        :return: scores for all players from this round
        """
        self.reset_for_new_round()
        self.deal(verbose=verbose)

        # check both players hand for the double value of the round
        for p in self.players:
            for t in p.hand:
                if t.is_double and t.low == self.round:
                    self.current_player = p
                    break
            if self.current_player:
                break
        
        print(self) # printing initial game state after selecting starting player
        print(f'Starting round {self.round}')

        round_done = False
        while not round_done:
            self.current_player.play_turn()
            if len(self.current_player.hand) == 0:
                round_done = True
            self.next_player()
        return [p.get_score() for p in self.players]

    def next_player(self) -> None:
        current_player_index = self.current_player.id
        next_player_index = (current_player_index + 1) % self.num_players
        self.current_player = self.players[next_player_index]

    def draw_tile(self, verbose=False) -> Tile:
        # Take a tile form boneyard and return it.  If boneyard empty, return None
        if self.boneyard:
            if verbose:
                print(f'Drawing tile from boneyard. {len(self.boneyard) - 1} tiles left.')
            return self.boneyard.pop(random.randint(0, len(self.boneyard) - 1))
        else:
            if verbose:
                print("Boneyard was empty when draw_tile was called.")
            return None

    def deal(self, verbose=False, ):
        for player in self.players:
            player.hand = [self.draw_tile(verbose=verbose) for _ in range(self.init_hand_size)]
            player.sort_hand()

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