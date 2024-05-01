from Qagent import QAgent
from Spinner import Spinner
import numpy as np
from matplotlib import pyplot as plt

def main():

    STATE_SPACE_MODELS = {1: 'one_state',
                          2: 'two_exposed_ends'}

    params = {'max_pips':           9,
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
    
    print('Initializing Spinner game with the following parameters:')
    print(params)
    print()
    game = Spinner(params)

    NUM_AGENTS = 10
    NUM_EPISODES = 2000
    ALPHA = 0.3
    EPSILON = 0.2
    GAMMA = 0.93
    EPS_TO_ZERO_AT = 750
    wins = [] # wins is a list of lists, [[0, 1, 0] ... [1, 1, 1]]
    print(f'Training {NUM_AGENTS} agents for {NUM_EPISODES} episodes with alpha={ALPHA}, epsilon={EPSILON}, gamma={GAMMA}, eps_to_zero_at={EPS_TO_ZERO_AT}')
    print()
    for a in range(NUM_AGENTS):
        agent = QAgent(game, alpha=ALPHA, epsilon=EPSILON, gamma=GAMMA, eps_to_zero_at=EPS_TO_ZERO_AT, verbose=False)
        print(f'Agent {a} learning...')
        wins.append(agent.learn(NUM_EPISODES))

    print()
    print('Finished training agents, plotting...')

    ROLLING_WINDOW = 100
    plot_wins(params, wins, ROLLING_WINDOW, NUM_AGENTS, NUM_EPISODES, ALPHA, EPSILON, GAMMA, EPS_TO_ZERO_AT)
    

def plot_wins(params, wins, rolling_window, num_agents, num_episodes, alpha, epsilon, gamma, eps_to_zero_at):
    
    # for each agent, get the rolling average of wins
    rolling_wins = []
    for a in range(num_agents):
        rolling_wins.append(np.convolve(wins[a], np.ones((rolling_window,))/rolling_window, mode='valid'))

    # get the average of the rolling averages
    avg_rolling_wins = np.mean(rolling_wins, axis=0)

    # find the max average rolling wins
    max_avg_rolling_wins = np.max(avg_rolling_wins)
    max_avg_rolling_wins_index = np.argmax(avg_rolling_wins)

    print(f'Percentage of wins for the last {rolling_window} episodes: {avg_rolling_wins[-1]}')
    print(f'Max Average Rolling Wins: {max_avg_rolling_wins} at episode {max_avg_rolling_wins_index}')

    # plot the average rolling wins
    plt.figure(figsize=(10, 5)) # make the plot bigger
    plt.plot(avg_rolling_wins)
    plt.title(f'Rolling Average Win Rate for {num_agents} Agents for {num_episodes} episodes ' + '\n' + f'Alpha: {alpha}, Epsilon: {epsilon}, Gamma: {gamma}, Eps_to_Zero_at: {eps_to_zero_at}, Rolling Window: {rolling_window}', fontsize=12)
    plt.xlabel('Episode', fontsize=12)
    plt.ylabel('Percentage Wins', fontsize=12)
    plt.axhline(y=0.5, color='g', linestyle='--') # add a horizontal line at 0.5

    # vertical line at eps_to_zero_at
    plt.axvline(x=eps_to_zero_at, color='g', linestyle='--')

    # vertical line at the max average rolling wins
    plt.axvline(x=max_avg_rolling_wins_index, color='r', linestyle='--')
    plt.text(max_avg_rolling_wins_index, max_avg_rolling_wins, f'Max: {max_avg_rolling_wins * 100:.2f}%', fontsize=12)
    # save the plot with the parameters in the filename
    plt.savefig(f'figures/avg_rolling_wins_{num_agents}_agents_{num_episodes}_episodes_alpha_{alpha}_epsilon_{epsilon}_gamma_{gamma}_eps_to_zero_at_{eps_to_zero_at}.png')
    plt.show()



if __name__ == '__main__':
    main()