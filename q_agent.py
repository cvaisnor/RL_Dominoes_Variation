# class of basic Q-learning agent
import numpy as np
import random
from classes import Player, Game

class QAgent(Player):
    def __init__(self, id, game, verbose=False):
        super().__init__(id, verbose)
        self.environment = game
        self.num_states = 
        self.num_actions = game.get_number_of_actions()
        self.Q = np.zeros((self.num_states, self.num_actions))
        self.N = np.zeros((self.num_states, self.num_actions))
        self.epsilon = 0.15
        self.gamma = 1
        
    def select_action(self, state):
        '''Selects an action using an epsilon-greedy policy'''
        if random.random() < self.epsilon:
            return random.randint(0, 1)
        else:
            return np.argmax(self.Q[state])