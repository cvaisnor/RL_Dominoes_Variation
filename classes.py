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

    def reset_hand(self):
        self.hand = []

    def play_turn(self, agent_action=None):

        """
        Method to play a turn.  Plays autonomously for all strategies except agent
        For agent, must be passed with action.  For other strategies action argument is ignored.
        Args:
            agent_action: action to be taken by agent.

        Returns: None

        """

        # limit turns for debugging
        if self.max_turns:
            if self.max_turns > 1:
                self.max_turns -= 1
            elif self.max_turns == 1:
                quit()

        # get available actions
        available_actions = self.get_available_actions()

        # check that action is passed if strategy == agent
        if self.strategy == 'agent':
            if agent_action is None and len(available_actions) > 1:
                raise Exception('Cannot execute play_turn() for strategy agent without with action = None')
        else:
            if agent_action is not None:
                raise Exception(f'Cannot execute play_turn() for strategy {self.strategy} if action = {agent_action}')

        if self.verbose:
            print(f'\nPlayer {self.id} turn - Round: {self.game.round}\n'
                  f'Boneyard: {self.game.boneyard_to_str()}\n'
                  f'{self.game.board}'
                  f'Hand: {self.hand_to_string()}\n'
                  f'Available Actions (Hand Index, Tile Value): {available_actions}')

        # choose an action if possible or draw a tile
        if available_actions:
            agent_action = self.choose_action(available_actions, agent_action)
            self.place_tile_from_hand(agent_action)
            if self.verbose:
                print(f'Player action {agent_action}\n'
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
                    and the value of the end of the tile to be played
        """
        available_actions = []
        if len(self.game.board.tiles) == 0:  # for empty board, find r|r or S|S
            r = self.game.round
            for index, tile in enumerate(self.hand):
                if tile.is_double and tile.high in [r, 'S']:
                    available_actions.append((index, r))
        else:  # after initial tile played
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
        :param action: tuple specify the index of the tile to play form the players hand and the exposed end
        oof the board on which the tile should be placed.
        :return: None
        """
        if len(self.hand) == 0:
            raise Exception(f'Player hand is empty, cannot place_tile_from_hand')
        tile_to_play = self.hand.pop(action[0])
        value_of_end_to_play = action[1]
        self.game.board.receive_tile(tile_to_play, value_of_end_to_play)

    def choose_action(self, action_list, agent_action):
        """
        This method takes a list of available actions and chooses one according to the assigned strategy for the player
        :param action_list:  A list of available actions for the players turn.  Actions are passed as tuples of
                                (index, end) where index is the index of the tile in the players hand
                                and end is the exposed end of the board on which the tile is to be played.
        :param agent_action: The action to be taken in the event the Player is an agent strategy type
        :return: action tuple as specified above
        """

        # if only one option available, return it
        if len(action_list) == 1:
            return action_list[0]

        match self.strategy:

            case 'random':
                return random.choice(action_list)

            case 'play_high':
                action_tile_values = [self.hand[i].value for i, _ in action_list]
                indices = [index for index, value in enumerate(action_tile_values) if value == max(action_tile_values)]
                max_actions = [action_list[i] for i in indices]
                return random.choice(max_actions)

            case 'play_low':
                action_tile_values = [self.hand[i].value for i, _ in action_list]
                indices = [index for index, value in enumerate(action_tile_values) if value == min(action_tile_values)]
                min_actions = [action_list[i] for i in indices]
                return random.choice(min_actions)

            case 'human':
                # print(f'Available ends: {self.game.board.exposed_ends}')
                # print(f'Player Hand is {self.hand_to_string()}')
                output = ' '.join([f'{i}-{self.hand[a[0]]}-[{a[1]}]  ' for i, a in enumerate(action_list)])
                print(f'Available actions: {output}')
                while True:
                    choice = int(input('Please enter index of chosen available action: '))
                    if choice in list(range(len(action_list))):
                        return action_list[choice]
                    print(f'Invalid choice. Please try again.')

            case 'agent':
                return agent_action

            case _:
                raise ValueError(f'Undefined player strategy {self.strategy}')

    def need_agent_input(self):
        return self.strategy == 'agent' and len(self.get_available_actions()) >= 2

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
                raise Exception(
                    f'Receive tile error, round {r} tile {len(self.tiles)} must have {r} or S end,'
                    f'passed tile is {tile}'
                )
            self.add_tile_adjust_exposed_ends(tile, end_value)
            if len(self.tiles) == 3 and self.allow_chickenfeet:
                self.exposed_ends += [r, r]

        else:  # fourth tile or later
            if self.exposed_double:
                if self.exposed_double_count <= self.tiles_per_double:
                    self.exposed_double_count += 1
                    if self.exposed_double_count == self.tiles_per_double:
                        self.exposed_double = None
                        self.exposed_double_count = 0
                    self.add_tile_adjust_exposed_ends(tile, end_value)

            elif tile.is_double:
                self.exposed_double = end_value  # end_value works for double spinner or double number
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
            raise Exception(
                f'Board.receive_tile error. add_tile_adjust_exposed_ends cannot receive double.  tile={tile}')
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
        if len(self.tiles) in [1, 2]:
            return [self.game.round]
        else:
            return sorted(list(set(self.exposed_ends)))

    def __str__(self):
        return (f'Board Tiles: {" ".join(map(str, self.tiles))}\n'
                f'Exposed ends: {self.exposed_ends}\n')


class Game(object):
    def __init__(self, params):

        # Load environment parameters that will not change
        self.params = params
        self.num_players = len(params['players'])
        self.max_pips = params['max_pips']
        self.spinners = params['spinners']
        self.allow_chickenfeet = params['allow_chickenfeet']
        self.verbose = params['verbose']

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
        self.round = self.starting_round
        self.scores_by_round = np.zeros((self.starting_round + 1, self.num_players))
        self.board.reset_for_new_round()
        for p in self.players:
            p.reset_hand()
        self.boneyard = self.tile_master.copy()
        self.deal()
        self.current_player = random.choice(self.players)

    def execute_action(self, action):
        if self.current_player.strategy != 'agent':
            raise Exception('Cannot execute action unless current player is agent')
        self.current_player.play_turn(action)
        self.update_game_and_round_done()
        self.next_player()
        while not self.game_done and not self.current_player.need_agent_input():
            self.current_player.play_turn()
            self.update_game_and_round_done()
            self.next_player()
            if self.round_done and not self.game_done:
                self.setup_new_round()
        return self.get_state(), self.get_reward(), self.game_done

    def get_state(self, state_type='basic'):
        if state_type == 'basic':
            return self.board.get_usable_exposed_ends()
            # return
        if state_type == 'vaisnorsamazingidea':
            pass

    def get_reward(self):
        if self.game_done and self.find_game_winner_index() == 0:
            return 100
        return 0

    def get_available_actions(self):
        return [0, 1, 2]

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
                if len(player.get_available_actions()) > 0:
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
