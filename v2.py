import random
import numpy as np


class QAgent:
    def __init__(self, alpha=0.3, gamma=0.3, epsilon=0.5):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rewards = []
        self.actions = [0, 1] # play_low, play_high
        self.q_table = np.zeros((16, 2))

    def choose_action(self, valid_moves):
        '''This function chooses an action based on the epsilon-greedy policy.
        Args:
            valid_moves (list): A list of indices of the tiles in the player's hand that can be played.
        Returns:
            int: The index of the tile in the player's hand that the player wants to play.
        '''
        action_map = {0: 'play_low', 1: 'play_high'}
        # assign the first valid move to play_low and the last valid move to play_high
        play_low = valid_moves[0]
        play_high = valid_moves[-1]

        # play low is the first column in the Q-table, play high is the second column
        
        if np.random.uniform(0, 1) < self.epsilon:
            tile_index_action = random.choice(valid_moves) # choose a random index from the valid moves
        else:
            # choose the action with the highest Q-value
            if self.q_table[play_low][0] > self.q_table[play_high][1]:
                print('Choosing play_low')
                tile_index_action = play_low
            else:
                print('Choosing play_high')
                tile_index_action = play_high
        return tile_index_action, action_map[0] if tile_index_action == play_low else action_map[1]
    
    def learn(self, state, action, reward, next_state, action_choosen):
        '''This function updates the Q-table using the Q-learning algorithm.'''
        # update the Q-value for the current state and action
    
        if action_choosen == 'play_low':
            # old_value = self.q_table[action][0]
            # print('Old Q Value: ', old_value)
            self.q_table[action][0] = self.q_table[action][0] + self.alpha * (reward + self.gamma * np.max(self.q_table[next_state]) - self.q_table[action][0])
            # print('New Q Value: ', self.q_table[action][0])
        else:
            # old_value = self.q_table[action][1]
            # print('Old Q Value: ', old_value)
            self.q_table[action][1] = self.q_table[action][1] + self.alpha * (reward + self.gamma * np.max(self.q_table[next_state]) - self.q_table[action][1])
            # print('New Q Value: ', self.q_table[action][1])

    def print_q_table(self):
        print(self.q_table)


class Player(QAgent):
    def __init__(self, id):
        '''This inherits from the QAgent class and initializes the player's hand and the actions they can take.'''
        super().__init__()
        self.hand = []
        
    def sort_hand(self):
        '''This sorts the player's hand in ascending order based on the sum of each inner list.'''
        self.hand.sort(key=lambda x: x[0] + x[1])

    def draw_tile(self, boneyard):
        if boneyard:
            tile = random.choice(boneyard)
            self.hand.append(tile)
            boneyard.remove(tile)

    def find_valid_moves(self, game_state, board) -> list[int]:
        '''This function finds the valid moves the player can make based on the current state of the game.
        Args:
            game_state (list): The exposed ends of the board.
            board (list): The current board.
        Returns:
            list[int]: A list of indices of the tiles in the player's hand that can be played.
        '''
        valid_moves = []

        # if the board is empty, find the highest double in the hand
        if not board:
            highest_double = -1
            for i, tile in enumerate(self.hand):
                if tile[0] == tile[1] and tile[0] > highest_double:
                    valid_moves.append(i)
                    highest_double = tile[0]

            # if there are multiple doubles, find the highest double
            if len(valid_moves) > 1:
                highest_double = -1
                for i in valid_moves:
                    if self.hand[i][0] > highest_double:
                        valid_moves = [i]
                        highest_double = self.hand[i][0]
            return valid_moves
        
        # if the board is not empty, find all the tiles that can be played
        for i, tile in enumerate(self.hand):
            if tile[0] == game_state[0] or tile[1] == game_state[0] or tile[0] == game_state[1] or tile[1] == game_state[1]:
                valid_moves.append(i)
        return valid_moves


class GameEnvironment:
    def __init__(self, lower_bound=0, upper_bound=3, num_players=2):
        self.players = [Player(i) for i in range(num_players)]
        self.boneyard = []
        self.board = []
        self.current_state = [None, None]
        self.current_player = None
        self.game_over = False
        self.num_of_actions = 3
        self.num_of_states = (upper_bound + 1) ** 2
        self.generate_tiles(lower_bound, upper_bound)

    def generate_tiles(self, lower_bound, upper_bound):
        self.tiles = []
        for i in range(lower_bound, upper_bound + 1):
            for j in range(i, upper_bound + 1):
                self.tiles.append([i, j])

    def reset(self, num_to_draw=3):
        self.boneyard = list(self.tiles)
        self.board = []
        self.current_state = [None, None]
        self.current_player = None
        self.game_over = False
        for player in self.players:
            player.hand = []
            for _ in range(num_to_draw):  # Draw tiles
                player.draw_tile(self.boneyard)
        self.determine_starting_player()

    def determine_starting_player(self):
        highest_double = -1
        for i, player in enumerate(self.players):
            for tile in player.hand:
                if tile[0] == tile[1] and tile[0] > highest_double:
                    self.current_player = i
                    highest_double = tile[0]
        if self.current_player is None:
            self.current_player = 0  # Default to player 0 if no double

    def get_state(self):
        return self.current_state

    def switch_player(self):
        # modulo switch between up to N players
        self.current_player = (self.current_player + 1) % len(self.players)

    def execute_action(self, action: int) -> tuple[list, int, bool]:
        '''The function removes the tile from the player's hand and adds it the board at the location where the tile matches the end of the board.
        Args:
            action (int): The index of the tile in the player's hand that the player wants to play.
        Returns:
            tuple[list], int, bool]: state(the exposed ends of the board), reward, done
        '''
        
        player = self.players[self.current_player]
        tile = player.hand.pop(action)
        # reward is the sum of the tile they got rid of
        reward = sum(tile)
        if not self.board:
            self.board.append(tile)
            self.current_state = [tile[0], tile[1]]
        else:
            ends = self.current_state
            if tile[0] == ends[0] or tile[1] == ends[0]: # front of list
                # check if the tile needs to be flipped
                if tile[1] == ends[0]:
                    self.board.insert(0, tile)
                else:
                    self.board.insert(0, [tile[1], tile[0]])
            elif tile[0] == ends[1] or tile[1] == ends[1]: # back of list
                # check if the tile needs to be flipped
                if tile[1] == ends[1]:
                    tile = [tile[1], tile[0]]    
                self.board.append(tile)
            self.current_state = [self.board[0][0], self.board[-1][1]]
        if not player.hand: # If the player has no tiles left, the game is over
            return self.current_state, 100, True
        
        # reward is the sum of the tile they got rid of
        return self.current_state, reward, False

    def play_game(self, num_to_draw=3, num_episodes=5):
        '''This function plays the game for a specified number of episodes.'''
        player_0_wins = 0
        player_1_wins = 0
        
        for episode in range(num_episodes):
            print('Starting episode', episode)
            self.reset(num_to_draw=num_to_draw)
            game_over = False
            max_draws = len(self.tiles)
            draw_count = 0
            while not game_over:
                # print('Environment State:')
                # print(f"Player {self.current_player}'s turn")
                for i, player in enumerate(self.players):
                    # sort the hand
                    player.sort_hand()
                    # only print the current player's hand
                    # if i == self.current_player:
                        # print(f'Player {i} Hand: {player.hand}')
                # print("Board: ", self.board)
                # print("Boneyard: ", self.boneyard)
                # print("Current State: ", self.current_state)
                valid_moves = self.players[self.current_player].find_valid_moves(self.current_state, self.board)
                if not valid_moves:
                    # print(f'No valid moves, player {self.current_player} draws a tile')
                    self.players[self.current_player].draw_tile(self.boneyard)
                    draw_count += 1
                    if draw_count == max_draws:
                        print('Max draws reached, game over')
                        break
                    # re-sort the hand
                    self.players[self.current_player].sort_hand()
                    # check if the player can play the tile they drew
                    valid_moves_after_draw = self.players[self.current_player].find_valid_moves(self.current_state, self.board)
                    if not valid_moves_after_draw:
                        print(f'Player {self.current_player} still cannot play, switching players')
                    else:
                        # execute the action
                        tile_index_action = valid_moves_after_draw[0]
                        new_state, reward, game_over = self.execute_action(tile_index_action)
                        # print(f'Action: {tile_index_action} - Reward: {reward} - New State: {new_state}')
                
                if len(valid_moves) == 1:
                    tile_index_action = valid_moves[0]
                    new_state, reward, game_over = self.execute_action(tile_index_action)
                    # print(f'Action: {tile_index_action} - Reward: {reward} - New State: {new_state}')
                
                #### Start Agent Step ####
                if len(valid_moves) > 1:
                    print(f'Multiple valid moves: {valid_moves}')
                    tile_index_action, action_choosen = self.players[self.current_player].choose_action(valid_moves)

                    print('Agent chooses tile index: ', tile_index_action, ' - Action: ', action_choosen)
                    new_state, reward, game_over_new = self.execute_action(tile_index_action)
                    # use the agent's learn method to update its Q-table
                    print('Updating Q-table')
                    self.players[self.current_player].learn(self.current_state, tile_index_action, reward, new_state, action_choosen)
                    self.players[self.current_player].print_q_table() # print the Q-table

                    print(f'Action: {tile_index_action} - Reward: {reward} - New State: {new_state}')
                    # now update the game_over variable
                    game_over = game_over_new
                    #### End Agent Step ####
                    
                self.switch_player() # switch player
                # print('-------------------------------------')
            
            print('Game Over')
            print(f'Player {self.current_player} wins')
            if self.current_player == 0:
                player_0_wins += 1
            else:
                player_1_wins += 1
            # print('-------------------------------------')
            print()
            print()
        
        print('Player 0 wins: ', player_0_wins)
        # print the Q-table for player 0
        self.players[0].print_q_table()
        print()
        print('Player 1 wins: ', player_1_wins)
        # print the Q-table for player 1
        self.players[1].print_q_table()




def main():
    tiles_lower_bound = 0
    tiles_upper_bound = 9
    
    num_rounds = 1000
    num_players = 2
    number_of_tiles_to_draw = 5

    game = GameEnvironment(tiles_lower_bound, tiles_upper_bound, num_players)
    game.play_game(number_of_tiles_to_draw, num_rounds)

if __name__ == '__main__':
    main()
