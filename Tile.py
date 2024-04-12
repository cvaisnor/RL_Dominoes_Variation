"""This script contains the classes used in the Spinner game."""


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
