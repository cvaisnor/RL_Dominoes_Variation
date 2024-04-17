from Qagent import QAgent
from Spinner import Spinner
import numpy as np


def main():


    params = {'max_pips':           9,
              'spinners':           False,
              'allow_chickenfeet':  False,
              'initial_hand_size':  7,
              'end_round':          0,
              'state_type':         'two_exposed_ends',
              'action_space_type':  'hrl',
              'players': [{'id': 0, 'strategy': 'agent', 'verbose': True},
                          {'id': 1, 'strategy': 'random', 'verbose': True},
                          ],
              'verbose': True}

    
    game = Spinner(params)

    agent = QAgent(game)
    print(agent.learn(1000))

if __name__ == '__main__':
    main()