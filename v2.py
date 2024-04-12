import random

class Player:
    def __init__(self, id):
        self.id = id
        self.hand = []
        self.actions = {'play_low': 0, 'play_random': 1, 'play_high': 2}
    
    def draw_tile(self, boneyard):
        if boneyard:
            tile = random.choice(boneyard)
            self.hand.append(tile)
            boneyard.remove(tile)

    def find_valid_moves(self, game_state, board):
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

    def execute_action(self, action: int) -> tuple[int, int, bool]:
        '''The function removes the tile from the player's hand and adds it the board at the location where the tile matches the end of the board.
        Returns:
            tuple[int, int, bool]: state(This is the exposed ends of the board), reward, done
        '''
        # print('Inside execute_action:')
        player = self.players[self.current_player]
        tile = player.hand.pop(action)
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
        return self.current_state, 0, False

    def play_game(self, num_to_draw=3):
        self.reset(num_to_draw=num_to_draw)
        game_over = False
        while not game_over:
            print('Environment State:')
            print(f"Player {self.current_player}'s turn")
            for i, player in enumerate(self.players):
                print(f'Player {i} hand: {player.hand}')
            print("Board: ", self.board)
            # print("Boneyard: ", self.boneyard)
            print("Current State: ", self.current_state)
            
            valid_moves = self.players[self.current_player].find_valid_moves(self.current_state, self.board)
            # print('Valid Moves: ', valid_moves)
            
            if not valid_moves:
                print('No valid moves')
                # draw a tile from the boneyard
                print(f'Player {self.current_player} draws a tile from the boneyard')
                print()
                self.players[self.current_player].draw_tile(self.boneyard)
                self.switch_player() # switch player
                continue
            
            chosen_action = random.choice(valid_moves) 
            print()
            current_state, reward, game_over = self.execute_action(chosen_action)
            if game_over:
                print('Game Over')
                print(f'Player {self.current_player} wins')
                break

            self.switch_player()


def main():
    game = GameEnvironment()
    game.play_game()

if __name__ == "__main__":
    main()
