import numpy as np

class BasePlayer:
    def set_n(self,n):
        self.n = n
    
    def reset_metrics(self):
        self.wins = 0
        self.losses = 0
        self.ties = 0
        
    def record_outcome(self, outcome):
        if outcome == self.n:
            self.wins += 1
        elif outcome == -self.n:
            self.losses += 1
        else:
            self.ties += 1
            
    def reset(self):
        pass
            
    def __str__(self):
        return self.__class__.__name__         

class EmptyPlayer(BasePlayer):
    def move(self, game, state):
        pass

    def update(self, game, state, reward):
        pass

    def __str__(self):
        return 'I do nothing'

class RandomPlayer(BasePlayer):
    def move(self, game, state):
        return game.sample()

    def update(self, game, state, reward):
        pass

    def __str__(self):
        return 'I make random moves'

class HumanPlayer(BasePlayer):
    def move(self, game, state):
        print(game)
        return int(input())

    def update(self, game, state, reward):
        if reward != 0:
            print('Human player received a reward',reward)

    def __str__(self):
        return 'I am a human player'

class ProceduralPlayer(BasePlayer):    
    def __init__(self):
        pass
    
    def move(self, game, state):
        move = self.winning_move(game)
        if move != 0:
            return move
        move = self.block_opponent(game)
        if move != 0:
            return move
        return game.sample()

    def winning_move(self, game):
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == 0:
                    game.board[row][col] = self.n
                    max_min = game.max_min()
                    game.board[row][col] = 0
                    if max_min[0] == self.n * 3:
                        return row * 3 + col
        return 0

    def block_opponent(self, game):
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == 0:
                    game.board[row][col] = -self.n
                    max_min = game.max_min()
                    game.board[row][col] = 0
                    if max_min[1] == -self.n * 3:
                        return row * 3 + col
        return 0
        
    def update(self, board, state, reward):
        pass
    
    def __str__(self):
        return 'Pretty good procedural player'
    
class Game:
    def __init__(self, x_player = EmptyPlayer(), o_player = EmptyPlayer()):
        self.x_player = x_player
        self.o_player = o_player
        self.i = 0
        self.reset()
        
    def reset(self):
        self.board = np.zeros([3,3])
        self.moves = 0
        self.x_turn = True     
        self.x_player.reset() 
        self.o_player.reset()

    # returns the max and min of sum of each axis + each diagonal
    def max_min(self):
        col_sum = np.sum(self.board,0)
        row_sum = np.sum(self.board,1)
        maxs = np.maximum(col_sum,row_sum)
        mins = np.minimum(col_sum,row_sum)
        diag0 = self.board.trace(0)
        diag1 = np.flip(self.board,0).trace(0)
        return max(max(maxs), diag0, diag1), min(min(mins), diag0, diag1)

    def is_empty(self, action):
        return self.board[action//3][action%3] == 0
    
    def move(self, action, player):
        n_player = 1 if player is self.x_player else -1
        row = action // 3
        col = action % 3
        if self.board[row][col] == 0:
            self.board[row][col] = n_player
            self.moves += 1
        else:
            raise ValueError("illegal move")
        x,o = self.max_min()
        return x == 3 or o == -3

    def is_empty(self, row_col):
        return self.board[row_col // 3,row_col % 3] == 0

    # return a random legal move (do not call if all 9 squares are taken!)
    def sample(self):
        if self.moves == 9:
            raise ValueError('cannot sample; board is full')
        while True:
            row = np.random.randint(3)  # 0,1,2
            col = np.random.randint(3)
            if self.board[row][col] == 0:
                return row * 3 + col

    def state(self, player):
        i = 0
        n = 1 if player is self.x_player else -1
        for row in range(3):
            for col in range(3):
                i += (n * self.board[row][col] + 1) * (3 ** (row*3+col))
        return int(i)

    def play(self):
        self.reset()
        self.i+=1       
        self.x_player.set_n(1)      
        self.o_player.set_n(-1)

        while self.moves < 9:
            player = self.x_player if self.x_turn else self.o_player
            opponent = self.o_player if self.x_turn else self.x_player
            state = self.state(player)
            winner = 0
            try:
                m = player.move(self,state)
                if self.move(m,player):
                    player.update(self,state,1)
                    opponent.update(self,state,-1)
                    winner = player.n
                    break
            except ValueError:
                player.update(self,state,-10)
                winner = -player.n
                break
            self.x_turn = not self.x_turn
        self.x_player.record_outcome(winner)
        self.o_player.record_outcome(winner)

    def __str__(self):
        s = '------------------------------------------\n'
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 1:
                    s += 'X'
                elif self.board[i][j] == -1:
                    s += 'O'
                else:
                    s += '-'
                s += '  '
            s += '\n\n'
        s += 'x state = '
        s += str(self.state(self.x_player))
        s += ', o state = '
        s += str(self.state(self.o_player))
        return s
