from Qagent import QAgent
from Spinner import Spinner
import numpy as np
from matplotlib import pyplot as plt


def main():

    STATE_SPACE_MODELS = {1: 'one_state',
                          2: 'two_exposed_ends'}

    params = {'max_pips':           5,
              'spinners':           False,
              'allow_chickenfeet':  False,
              'initial_hand_size':  7,
              'end_round':          0,
              'state_type':         STATE_SPACE_MODELS[2],
              'action_space_type':  'hl',
              'players': [{'id': 0, 'strategy': 'agent', 'verbose': False},
                          {'id': 1, 'strategy': 'random', 'verbose': False},
                          #{'id': 2, 'strategy': 'random', 'verbose': False},
                          ],
              'verbose': False}


    
    game = Spinner(params)

    AGENTS = 10
    EPISODES = 2000
    ALPHA = 0.3
    EPSILON = 0.2
    GAMMA = 0.99
    EPS_TO_ZERO_AT = None
    wins = np.zeros((AGENTS, EPISODES))
    for a in range(AGENTS):
        agent = QAgent(game, alpha=ALPHA, epsilon=EPSILON, gamma=GAMMA, eps_to_zero_at=EPS_TO_ZERO_AT, verbose=False)
        wins[a, :] = agent.learn(episodes=EPISODES)

    win_percentages = wins.cumsum(axis=1) / (np.arange(wins.shape[1]) + 1)

    avg_win_percentages = np.mean(win_percentages, axis=0)
    plt.figure(figsize=(8, 4))
    plt.plot(avg_win_percentages)
    plt.axhline(y=0.5, color='r', linestyle='--')
    if EPS_TO_ZERO_AT:
        plt.axvline(x=EPS_TO_ZERO_AT, color='g', linestyle='--')
    plt.ylim([0, 1])
    plt.xlabel('Episodes')
    plt.ylabel('Average win percentage')
    plt.title(f'Average win percentage for {AGENTS} agents\n'
              f'\u03B1: {ALPHA}  \u03f5: {EPSILON}  \u03B3: {GAMMA}  \u03F5\u21920 @ {EPS_TO_ZERO_AT}\n'
              f'State Model: {params["state_type"]}  Action Model: {params["action_space_type"]}',
                 fontsize=12)
    plt.subplots_adjust(top=.8)

    plt.show()

    # wins_per_last_30 = rolling_sum(np.mean(wins, axis=0), 100)
    # plt.plot(wins_per_last_30)
    # plt.show()




def rolling_sum(array, window):
    """
    Accepts a numpy array and a window size and returns a numpy array that is a rolling sum of size window.
    The first window elements are the cumulative sum of the elements in the array
    """
    return np.convolve(array, np.ones(window), 'full')[:len(array)]

if __name__ == '__main__':
    main()