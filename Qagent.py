"""
705.741
Q-Learning Agent
Author: Harris Rose
This code creates a Q-Learning agent for the Spinner environment.
"""

import random
import numpy as np


class QAgent:

    def __init__(self, env, alpha=0.1, epsilon=0.2, gamma=0.9, verbose =True):
        self.env = env
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.verbose = verbose
        self.num_actions = self.env.get_num_actions()
        self.num_states = self.env.get_num_states()
        self.q_table = np.zeros((self.num_states, self.num_actions))
        self.n_table = np.zeros((self.num_states, self.num_actions))

    def generate_episode(self):
        # implement Q-Learning algorithm
        total_reward = 0
        win = False
        current_state, reward, terminal = self.env.reset()

        if self.verbose:
            print(f'Generating New Episode Current State, reward, term: {current_state} {reward} {terminal}')

        while not terminal:
            action = self.choose_action_e_greedy(current_state)
            new_state, reward, terminal = self.env.execute_action(action)
            if self.verbose:
                print(f'Executing action: {action} New State, reward, terminal: {new_state} {reward} {terminal}')
            self.q_table[current_state, action] += self.alpha * (reward + self.gamma * self.q_table[new_state].max() -
                                                                 self.q_table[current_state, action])
            self.n_table[current_state, action] = 1
            if self.verbose:
                print(self.q_table)
            total_reward += reward  # TODO Chris says this may be the problem!!!
            if reward == 100:
                win = True
            current_state = new_state
        return total_reward, win

    def learn(self, episodes=1000):
        rewards = np.empty(episodes)
        wins = np.empty(episodes)

        for i in range(episodes):
            reward, win = self.generate_episode()
            rewards[i] = reward
            wins[i] = 1 if win else 0
            if i == 750:
                self.epsilon = 0.

        return self.q_table, rewards, wins

    def choose_action_e_greedy(self, state):
        if random.random() < self.epsilon:
            return np.random.randint(self.num_actions)
        else:
            q_values = self.q_table[state]
            max_q = np.max(q_values)
            actions = np.where(q_values == max_q)[0]
            return np.random.choice(actions)
