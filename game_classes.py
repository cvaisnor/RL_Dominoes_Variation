'''This script contains the classes used in the Spinner game.'''

import numpy as np

class Tile(object):
    def __init__(self,num1,num2):
        self.num1=num1
        self.num2=num2
        self.is_spinner = False
        if num1 == 'spinner' or num2 == 'spinner':
            self.is_spinner = True

    def __str__(self):
        return str(self.num1)+'-'+str(self.num2)    

class Game(object):
    def __init__(self):
        self.round = 9 # start at round 9 and count down
        self.current_player = 0 # start with player 0
        self.players = []
        self.tiles_in_vault = [] # tiles that are not in the players' hands or already played
        self.board = [[] for i in range(3)] # max 3 branches

    def create_tile_set(self, max_tile=9, include_spinners=True) -> None:
        for tile in range(0, max_tile+1):
            for i in range(tile, max_tile+1):
                self.tiles_in_vault.append(Tile(tile,i))
        
        if include_spinners:
            # add the spinner tiles, one for each number
            for i in range(0, max_tile+1):
                self.tiles_in_vault.append(Tile('spinner',i))
            
            # add the double spinner tile
            self.tiles_in_vault.append(Tile('spinner','spinner'))

    def deal_tiles(self, num_tiles=3) -> None:
        for i in range(num_tiles):
            for player in self.players:
                player.draw_tile(self.tiles_in_vault)

    def shuffle_tiles(self) -> None:
        np.random.shuffle(self.tiles_in_vault)

    def add_tile_to_branch(self,branch,tile) -> None:
        # check if the move is valid
        if len(self.board[branch]) == 0:
            self.board[branch].append(tile)
        else:
            if tile.num1 == self.board[branch][0].num1 or tile.num2 == self.board[branch][0].num1:
                self.board[branch].insert(0,tile)
            elif tile.num1 == self.board[branch][-1].num2 or tile.num2 == self.board[branch][-1].num2:
                self.board[branch].append(tile)
            else:
                raise ValueError('Invalid move')
            
    def find_valid_moves(self,tile) -> list:
        valid_moves = []
        for i, chain in enumerate(self.board):
            if len(chain) == 0:
                valid_moves.append(i)
            elif tile.num1 == chain[0].num1 or tile.num2 == chain[0].num1:
                valid_moves.append(i)
            elif tile.num1 == chain[-1].num2 or tile.num2 == chain[-1].num2:
                valid_moves.append(i)
        return valid_moves

    def get_tiles_in_vault(self) -> list:
        return self.tiles_in_vault

    def reset():
        pass

    def next_player(self) -> None:
        print('The current player is:',self.current_player)
        self.current_player = (self.current_player + 1) % len(self.players)

    def start_game(self, players) -> None:
        # find highest double tile and the player who has it
        highest_double = 0
        player_with_highest_double = None
        for player in players:
            for tile in player.hand:
                if tile.num1 == tile.num2 and tile.num1 > highest_double:
                    highest_double = tile.num1
                    player_with_highest_double = player
        
        # set the current player to the one with the highest double
        self.current_player = player_with_highest_double

        highest_double = player.play_tile(tile)

        print('Player',player.name,'has the highest double tile:',highest_double.num1,highest_double.num2)

        # play the highest double tile and start the game
        self.board[0].append(highest_double)   


class Player(object):
    def __init__(self,name):
        self.name=name
        self.hand=[]
        self.score=0

    def draw_tile(self, available_tiles):
        # add a tile to the player's hand
        self.hand.append(available_tiles.pop())

    def play_tile(self,tile):
        self.hand.remove(tile)
        return tile

    def get_score(self):
        for tile in self.hand:
            if tile.is_spinner:
                self.score += 10
                if tile.num1 == 'spinner':
                    self.score += tile.num2
                else:
                    self.score += tile.num1
            else:
                self.score += tile.num1 + tile.num2
        return self.score