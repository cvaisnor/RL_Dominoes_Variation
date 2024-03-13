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
        self.available_tiles = [] # set of tiles that are not in the players' hands or on the board
        self.chains = [[] for i in range(6)]

    def create_tile_set(self):
        for tile in range(0,10):
            for i in range(tile,10):
                self.available_tiles.append(Tile(tile,i))
            
        # add the spinner tiles, one for each number
        for i in range(0,10):
            self.available_tiles.append(Tile('spinner',i))
        
        # add the double spinner tile
        self.available_tiles.append(Tile('spinner','spinner'))

    def deal_tiles(self, num_tiles=7):
        for i in range(num_tiles):
            for player in self.players:
                player.draw_tile(self.available_tiles)

    def shuffle_tiles(self):
        np.random.shuffle(self.available_tiles)

    def add_tile_to_chain(self,chain,tile):
        # check if the move is valid
        if len(self.chains[chain]) == 0:
            self.chains[chain].append(tile)
        else:
            if tile.num1 == self.chains[chain][0].num1 or tile.num2 == self.chains[chain][0].num1:
                self.chains[chain].insert(0,tile)
            elif tile.num1 == self.chains[chain][-1].num2 or tile.num2 == self.chains[chain][-1].num2:
                self.chains[chain].append(tile)
            else:
                raise ValueError('Invalid move')
            
    def find_valid_moves(self,tile):
        valid_moves = []
        for i, chain in enumerate(self.chains):
            if len(chain) == 0:
                valid_moves.append(i)
            elif tile.num1 == chain[0].num1 or tile.num2 == chain[0].num1:
                valid_moves.append(i)
            elif tile.num1 == chain[-1].num2 or tile.num2 == chain[-1].num2:
                valid_moves.append(i)
        return valid_moves
    
    def get_chains(self):
        pass

    def get_available_tiles(self):
        return self.available_tiles

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