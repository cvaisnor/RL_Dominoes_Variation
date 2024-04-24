"""
705.741
Q-Learning Agent
Author: Harris Rose
This code creates a Q-Learning agent for the Spinner environment.
"""

import random
import numpy as np


class QAgent:

    def __init__(self, env,
                 alpha=0.1,
                 epsilon=0.2,
                 gamma=0.9,
                 eps_to_zero_at = None,
                 verbose =True):
        self.env = env
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.verbose = verbose
        self.eps_to_zero_at = eps_to_zero_at
        self.num_actions = self.env.get_num_actions()
        self.num_states = self.env.get_num_states()
        self.q_table = np.zeros((self.num_states, self.num_actions))
        self.n_table = np.zeros((self.num_states, self.num_actions))

    def generate_episode(self, q_update=True):
        # implement Q-Learning algorithm
        win = False
        current_state, reward, terminal = self.env.reset()

        if self.verbose:
            print(f'Generating New Episode Current State, reward, term: {current_state} {reward} {terminal}')

        while not terminal:
            action = self.choose_action_e_greedy(current_state)
            new_state, reward, terminal = self.env.execute_action(action)
            if self.verbose:
                print(f'Executing action: {action} New State, reward, terminal: {new_state} {reward} {terminal}')
            if q_update:
                self.q_table[current_state, action] += self.alpha * (reward +
                                                                     self.gamma * self.q_table[new_state].max() -
                                                                     self.q_table[current_state, action])
            self.n_table[current_state, action] = 1
            if self.verbose:
                print(self.q_table)
            if reward == 100:
                win = True
            current_state = new_state
        return win

    def learn(self, episodes=1000):
        wins = np.empty(episodes)

        for i in range(episodes):
            win = self.generate_episode(q_update=True)
            wins[i] = 1 if win else 0
            if i == self.eps_to_zero_at:
                 self.epsilon = 0.

        return wins

    def exploit(self, episodes=1000):
        for i in range(episodes):
            wins = np.empty(episodes)
            reward, win = self.generate_episode(q_update=False)
            wins[i] = 1 if win else 0
            return wins

    def choose_action_e_greedy(self, state):
        if random.random() < self.epsilon:
            return np.random.randint(self.num_actions)
        else:
            q_values = self.q_table[state]
            max_q = np.max(q_values)
            actions = np.where(q_values == max_q)[0]
            return np.random.choice(actions)
