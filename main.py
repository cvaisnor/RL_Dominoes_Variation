from simple_game_classes import Game
import numpy as np


def main():


    params = {'max_pips':           5,
              'spinners':           False,
              'allow_chickenfeet':  False,
              'tiles_per_double':   1,
              'initial_hand_size':  7,
              'end_round':          0,
              'players': [{'id': 0, 'strategy': 'play_high', 'verbose': True},
                          {'id': 1, 'strategy': 'play_low', 'verbose': True},
                          ]}

    game = Game(params)
    print(f'Game scores by round')
    print(game.scores_by_round)
    print()
    print(f'Game total scores')
    print(game.total_scores)





if __name__ == '__main__':
    main()