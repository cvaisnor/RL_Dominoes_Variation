from game_classes import Tile, Game, Player

def main():

    game = Game()
    game.create_tile_set(max_tile=3, include_spinners=False)
    print('There are',len(game.tiles_in_vault),'tiles in the set')

    # shuffle the tiles
    game.shuffle_tiles()

    # create 3 players
    for i in range(3):
        game.players.append(Player(i))

    # have each player draw tiles
    game.deal_tiles(num_tiles=2)

    # show the hand of each player
    for player in game.players:
        print('Player',player.name,'has the following tiles:')
        for tile in player.hand:
            print(tile.num1,tile.num2)
        print()

    available_tiles = game.get_tiles_in_vault()
    print('The available tiles are:')
    for tile in available_tiles:
        print(tile.num1,tile.num2)
    
    # start the game
    game.start_game(game.players) # this will set the current player to the one with the highest double tile and place it on the board
    game.next_player()
    print('The current player is:',game.current_player)
    print('The board is:')
    for i, chain in enumerate(game.board):
        print('Chain',i)
        for tile in chain:
            print(tile.num1,tile.num2)
        print()

if __name__ == '__main__':
    main()