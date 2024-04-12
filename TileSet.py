"""This script contains the classes used in the Spinner game."""
import random
from itertools import combinations_with_replacement
from Tile import Tile


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
