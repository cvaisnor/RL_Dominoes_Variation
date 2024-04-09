from classes import Game
import numpy as np


def main():


    params = {'max_pips':           3,
              'spinners':           False,
              'allow_chickenfeet':  False,      # TODO debug chickenfeet
              'tiles_per_double':   1,
              'initial_hand_size':  3,
              'end_round':          2,
              'players': [{'id': 0, 'strategy': 'play_high', 'verbose': True},
                          {'id': 1, 'strategy': 'play_low', 'verbose': True},
                          ]}
    
    game = Game(params)
    print('Game initialized w/ params')
    print(params)
    print('-'*50)

    game.play_round(verbose=True) # easier to debug game logic for single round
    print('Round Finished')

    # game.play_game(verbose=True) # this works, lot of output

    # print(f'Game scores by round')
    # print(game.scores_by_round)

    # print()
    # print(f'Game total scores')
    # print(game.total_scores)


if __name__ == '__main__':
    main()