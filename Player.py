"""This script contains the classes used in the Spinner game."""
import random
from typing import Union


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
        valid_plays = self.get_valid_plays()

        if self.verbose:
            print(f'\nPlayer {self.id} turn - Round: {self.game.round}\n'
                  f'Boneyard: {self.game.boneyard_to_str()}\n'
                  f'{self.game.board}'
                  f'Hand: {self.hand_to_string()}\n'
                  f'Available Actions (Hand Index, Tile Value): {valid_plays}')

        # action according to number of tiles that can be played
        match len(valid_plays):
            case 0:
                play = 'Draw'
                self.draw_tile_to_hand()
            case 1:
                play = valid_plays[0]
                self.place_tile_from_hand(play)
            case _:
                play = self.choose_valid_play(valid_plays, agent_action)
                self.place_tile_from_hand(play)

        if self.verbose:
            print(f'Strategy {self.strategy} play: {play} \n'
                  f'New Hand {self.hand_to_string()}\n')

    def choose_valid_play(self, valid_plays, agent_action=None):
        """
        This method takes a list of available actions and chooses one according to the assigned strategy for the player
        :param valid_plays:  A list of available actions for the players turn.  Actions are passed as tuples of
                                (index, end) where index is the index of the tile in the players hand
                                and end is the exposed end of the board on which the tile is to be played.
        :param agent_action: The action to be taken in the event the Player is an agent strategy type
        :return: action tuple as specified above
        """

        value_to_match = self.strategy
        if self.strategy == 'agent':
            if agent_action is None:
                raise Exception('Cannot choose_valid_play() for agent without with action = None')
            else:
                value_to_match = agent_action
        else:
            if agent_action is not None:
                raise Exception(f'Cannot choose_valid_play() for strategy {self.strategy} '
                                f'with with agent_action {agent_action} ')

        match value_to_match:
            case 'random':
                return random.choice(valid_plays)

            case 'play_high':
                return self.choose_high_low_tile(valid_plays, high=True)

            case 'play_low':
                return self.choose_high_low_tile(valid_plays, high=False)

            case 'human':
                output = ' '.join([f'{i}-{self.hand[a[0]]}-[{a[1]}]  ' for i, a in enumerate(valid_plays)])
                print(f'Available actions: {output}')
                while True:
                    choice = int(input('Please enter index of chosen available action: '))
                    if choice in list(range(len(valid_plays))):
                        return valid_plays[choice]
                    print(f'Invalid choice. Please try again.')
            case _:
                raise ValueError(f'choose_valid_play() - Undefined player strategy {self.strategy}')

    def get_valid_plays(self) -> list[tuple[int, Union[int, str]]]:
        """
        Method to search players hand for playable tiles given the playable exposed ends of the board
        :return: List of actions that are possible given a player's hand and the board's exposed tiles
                    Actions are tuples containing the index of a playable tile in the players hand
                    and the value of the end of the tile to be played
        """
        valid_plays = []
        if len(self.game.board.tiles) == 0:  # for empty board, find r|r or S|S
            r = self.game.round
            for index, tile in enumerate(self.hand):
                if tile.is_double and tile.high in [r, 'S']:
                    valid_plays.append((index, r))
        else:  # after initial tile played
            usable_exposed_ends = self.game.board.get_usable_exposed_ends()
            for index, tile in enumerate(self.hand):
                if not tile.is_double or len(self.game.board.tiles) > 2:  # Can't play double on plays 1 and 2
                    if tile.low in usable_exposed_ends:
                        valid_plays.append((index, tile.low))
                    if tile.high in usable_exposed_ends and not tile.is_double:
                        valid_plays.append((index, tile.high))
                    if tile.high == 'S':
                        for e in usable_exposed_ends:
                            valid_plays.append((index, e))
        return valid_plays

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

    def choose_high_low_tile(self, action_list, high):
        action_list_tile_values = [self.hand[i].value for i, _ in action_list]
        max_min_value = max(action_list_tile_values) if high else min(action_list_tile_values)
        indices = [i for i, v in enumerate(action_list_tile_values) if v == max_min_value]
        actions_chosen = [action_list[i] for i in indices]
        return random.choice(actions_chosen)

    def need_agent_input(self):
        return self.strategy == 'agent' and len(self.get_valid_plays()) >= 2

    def get_score(self):
        values = [t.value for t in self.hand]
        return sum(values)

    def sort_hand(self):
        self.hand.sort(key=lambda t: t.id)

    def hand_to_string(self):
        return ' '.join(map(str, self.hand)) if self.hand else 'Empty'

    def __str__(self):
        return f'Player {self.id} Hand {self.hand_to_string()}'
