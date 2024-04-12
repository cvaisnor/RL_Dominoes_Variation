from Qagent import QAgent
from Spinner import Spinner
import numpy as np


def main():


    params = {'max_pips':           9,
              'spinners':           False,
              'allow_chickenfeet':  False,
              'initial_hand_size':  5,
              'end_round':          5,
              'state_type':         'two_exposed_ends',
              'action_space_type':  'hrl',
              'players': [{'id': 0, 'strategy': 'agent', 'verbose': True},
                          {'id': 1, 'strategy': 'random', 'verbose': True},
                          ],
              'verbose': True}

    
    game = Spinner(params)



    # print('Game initialized w/ params')
    # print(params)
    # print('-'*50)
    #
    # game.play_game() # easier to debug game logic for single round

    agent = QAgent(game)
    print(agent.learn())

if __name__ == '__main__':
    main()