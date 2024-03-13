from game_classes import Tile, Game, Player
import numpy as np
import random
import copy

def main():

    board = Game()
    board.create_tile_set()
    print('There are',len(board.available_tiles),'tiles in the set')

    # shuffle the tiles
    board.shuffle_tiles()

    # create 3 players
    for i in range(3):
        board.players.append(Player(i))

    # have each player draw 7 tiles
    board.deal_tiles()

    # show the hand of each player
    for player in board.players:
        print('Player',player.name,'has the following tiles:')
        for tile in player.hand:
            print(tile.num1,tile.num2)
        print()
        print('Next player')

if __name__ == '__main__':
    main()