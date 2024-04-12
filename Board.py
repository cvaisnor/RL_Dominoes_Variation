"""This script contains the classes used in the Spinner game."""


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
            if tile.is_double:
                raise Exception(
                    f'Receive tile error, round {r} tile {len(self.tiles)} cannot be double,'
                    f'passed tile is {tile}'
                )
            self.add_tile_adjust_exposed_ends(tile, end_value)
            if len(self.tiles) == 3 and self.allow_chickenfeet:
                self.exposed_ends += [r, r]

        else:  # fourth tile or later
            if self.exposed_double:
                if self.exposed_double_count < self.tiles_per_double:
                    self.exposed_double_count += 1
                    if self.exposed_double_count == self.tiles_per_double:
                        self.exposed_double = None
                        self.exposed_double_count = 0
                    if tile.is_double:
                        self.tiles.append(tile)
                    else:
                        print(f'exp_double={self.exposed_double} exp ends={self.exposed_ends}')
                        self.add_tile_adjust_exposed_ends(tile, end_value)
                else:
                    raise Exception(f'Board.receive_tile error.'
                                    f'exposed double count >= tiles per double'
                                    f'')

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
        # TODO needs to address exposed doubles = True, can't remove double value from exposed ends
        self.tiles.append(tile)
        if tile.is_double:
            raise Exception(
                f'Board.receive_tile error. add_tile_adjust_exposed_ends cannot receive double.  tile={tile}\n'
                f'exposed_double={self.exposed_double}')
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
