import numpy as np

class Board:
    def __init__(self, x_player, o_player):
        self.x_player = x_player
        self.o_player = o_player

    def reset(self):
        self.board = np.zeros([3,3])
        self.moves = 0
        
    # returns the max and min of sum of each axis + each diagonal
    def max_min(self):
        col_sum = np.sum(self.board,0)
        row_sum = np.sum(self.board,1)
        maxs = np.maximum(col_sum,row_sum)
        mins = np.minimum(col_sum,row_sum)
        diag0 = self.board.trace(0)
        diag1 = np.flip(self.board,0).trace(0)
        return max(max(maxs), diag0, diag1), min(min(mins), diag0, diag1)

    # returns winner (if one player had won), else None
    def winner(self):
        x,o = self.max_min()
        if x == 3:
            return 1
        elif o == -3:
            return -1
        else:
            return 0

    def game_over(self, winner):
        return winner != 0 or self.moves == 9

    # record a move; return reward with respect to ai player
    def move(self, action, player):
        row = action // 3
        col = action % 3
        if self.board[row][col] == 0:
            self.board[row][col] = player
            self.moves += 1
        else:
            raise ValueError("Illegal move.")
        return self.winner()

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

    def state(self):
        i = 0
        for row in range(3):
            for col in range(3):
                i += (self.board[row][col] + 1) * (3 ** (row*3+col))
        return int(i)

    def play(self, verbose=False):
        self.reset()
        winner = 0
        while not self.game_over(winner):
            x_state = self.state()
            try:
                winner = self.move(self.x_player.move(self, x_state),1)
            except ValueError:
                winner = -1
            if verbose:
                print(self)
            if not self.game_over(winner):
                try:
                    winner = self.move(self.o_player.move(self, self.state()),-1)
                except ValueError:
                    winner = 1
                if verbose:
                    print(self)
            self.x_player.update(self, x_state, winner)
            self.o_player.update(self, self.state(), -winner)
            if verbose and self.game_over(winner):
                print("WINNER = ", self.winner())

    def __str__(self):
        s = '------------------------------------------\n'
        s += self.board.__str__()
        s += '\n------------------------------------------\n'
        s += 'x_player: '
        s += self.x_player.__str__()
        s += '\n'
        s += 'o_player: '
        s += self.o_player.__str__()
        return s

class RandomPlayer:
    def move(self, board, state):
        return board.sample()

    def update(self, board, state, reward):
        pass

    def __str__(self):
        return 'I make random moves'

class HumanPlayer:
    def move(self, board, state):
        return int(input())

    def update(self, board, state, reward):
        pass

    def __str__(self):
        return "I am a human player"
