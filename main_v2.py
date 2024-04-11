from v2 import GameEnvironment

def main():
    tiles_lower_bound = 0
    tiles_upper_bound = 3
    
    number_of_tiles_to_draw = 3

    game = GameEnvironment(tiles_lower_bound, tiles_upper_bound)
    game.play_game(number_of_tiles_to_draw)

if __name__ == '__main__':
    main()