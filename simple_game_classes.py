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
    id = 0

    def __init__(self, game, strategy, verbose=False, max_turns=None):
        self.game = game
        self.strategy = strategy
        self.hand = []
        self.verbose = verbose
        self.id = Player.id
        self.max_turns = max_turns
        Player.id += 1

    def play_turn(self):

        if self.max_turns:
            if self.max_turns>1:
                self.max_turns -= 1
            elif self.max_turns==1:
                quit()

        available_actions = self.get_available_actions()
        if self.verbose:
            print(f'\nPlayer {self.id} turn\n'
                  f'{self.game.board}'
                  f'Hand: {self.hand_to_string()}\n'
                  f'Available Actions: {available_actions}')
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
        available_actions = []
        if len(self.game.board.tiles) == 0:
            r = self.game.round
            for index, tile in enumerate(self.hand):
                if tile.is_double and tile.high in [r, 'S']:
                    available_actions.append((index, r))
        else:
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
        new_tile = self.game.draw_tile()
        if new_tile:
            self.hand.append(new_tile)
        else:
            print('Boneyard empty!!!!!!!!!!')
        self.sort_hand()

    def place_tile_from_hand(self, action):
        if len(self.hand) == 0:
            raise Exception(f'Player hand is empty, cannot place_tile_from_hand')
        tile_to_play = self.hand.pop(action[0])
        value_of_end_to_play = action[1]
        self.game.board.receive_tile(tile_to_play, value_of_end_to_play)

    def choose_action(self, action_list):
        if len(action_list) == 1:
            return action_list[0]

        if self.strategy == 'random':
            return random.choice(action_list)

        if self.strategy == 'play_high':
            action_tile_values = [self.hand[i].value for i, _ in action_list]
            indices = [index for index, value in enumerate(action_tile_values) if value == max(action_tile_values)]
            max_actions = [action_list[i] for i in indices]
            return random.choice(max_actions)

        if self.strategy == 'play_low':
            action_tile_values = [self.hand[i].value for i, _ in action_list]
            indices = [index for index, value in enumerate(action_tile_values) if value == min(action_tile_values)]
            min_actions = [action_list[i] for i in indices]
            return random.choice(min_actions)

        if self.strategy == 'manual':
            # print(f'Available ends: {self.game.board.exposed_ends}')
            # print(f'Player Hand is {self.hand_to_string()}')
            output = ' '.join([f'{i}-{self.hand[a[0]]}-[{a[1]}]  ' for i, a in enumerate(action_list)])
            print(f'Available actions: {output}')
            while True:
                choice = int(input('Please enter index of chosen available action: '))
                if choice in list(range(len(action_list))):
                    return action_list[choice]
                print(f'Invalid choice. Please try again.')

    def get_score(self):
        values = [t.value for t in self.hand]
        return sum(values)

    def sort_hand(self):
        self.hand.sort(key=lambda t: t.id)

    def hand_to_string(self):
        return ' '.join(map(str, self.hand))

    def __str__(self):
        return f'Player {self.id} Hand {self.hand_to_string()}'


class Board:
    def __init__(self, game, allow_chickenfeet=False):
        self.game = game
        self.tiles = []
        self.exposed_ends = []
        self.exposed_double = None
        self.exposed_double_count = 0
        self.tiles_per_double = 3 if allow_chickenfeet else 1

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
            if len(self.tiles) == 3:
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
        self.init_hand_size = 7

        self.max_round = self.max_pips  # start at round 9 and count down
        self.round = self.max_round
        self.min_round = params['end_round']
        self.rounds_to_play = self.max_round - self.min_round + 1
        self.scores_by_round = np.zeros((self.max_round + 1, self.num_players))
        self.total_scores = np.zeros((1, self.num_players))

        self.current_player = self.players[random.randint(0, self.num_players - 1)]

        self.deal()
        print('Setting up game and Dealing...')
        print(self)

        self.play_game()

    def reset(self):
        pass

    def execute_action(self):
        pass

    def get_state(self):
        pass

    def play_game(self):
        for self.round in range(self.max_round, self.min_round - 1, -1):
            round_scores = self.play_round()
            next_player_index = random.choice(
                [i for i, v in enumerate(round_scores) if v == max(round_scores)])
            self.scores_by_round[self.round] = round_scores
            self.current_player = self.players[next_player_index]
        self.total_scores = np.sum(self.scores_by_round, axis=0)

    def play_round(self):
        self.boneyard = self.tile_master.copy()
        self.board = Board(self, self.allow_chickenfeet)
        self.players = [Player(self, p['strategy'], p['verbose']) for p in self.params['players']]

        round_done = False
        boneyard_empties = 0
        while not round_done:
            self.current_player.play_turn()
            if len(self.current_player.hand) == 0 :
                round_done = True
            if len(self.boneyard) == 0:
                boneyard_empties += 1
            if boneyard_empties >= 10:
                round_done = True
            self.next_player()
        return [p.get_score() for p in self.players]

    def next_player(self):
        current_player_index = self.current_player.id
        next_player_index = (current_player_index + 1) % self.num_players
        self.current_player = self.players[next_player_index]

    def draw_tile(self):
        # Take a tile form boneyard and return it.  If boneyard empty, return None
        if self.boneyard:
            return self.boneyard.pop(random.randint(0, len(self.boneyard) - 1))
        else:
            print("Boneyard empty!!!!")
            return None

    def deal(self):
        for player in self.players:
            player.hand = [self.draw_tile() for _ in range(self.init_hand_size)]
            player.sort_hand()

    def boneyard_to_str(self):
        return ' '.join(map(str, self.boneyard))

    def __str__(self):
        hands = ''
        for p in self.players:
            hands += f'Player {p.id} Hand: {p.hand_to_string()}\n'

        return (f'Game Status:\n'
                f'Current Player: {self.current_player.id}\n'
                f'Boneyard: {self.boneyard_to_str()}\n'
                f'{self.board}'
                f'{hands}')
