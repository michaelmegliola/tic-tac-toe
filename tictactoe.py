import numpy as np

class EmptyPlayer:
    def move(self, game, state):
        pass

    def update(self, game, state, reward):
        pass

    def __str__(self):
        return 'I do nothing'

class RandomPlayer:
    def move(self, game, state):
        return board.sample()

    def update(self, game, state, reward):
        pass

    def __str__(self):
        return 'I make random moves'

class HumanPlayer:
    def move(self, game, state):
        print(game)
        return int(input())

    def update(self, game, state, reward):
        if reward != 0:
            print('Human player received a reward',reward)

    def __str__(self):
        return 'I am a human player'

class Game:
    def __init__(self, x_player = EmptyPlayer(), o_player = EmptyPlayer()):
        self.x_player = x_player
        self.o_player = o_player
        self.reset()
        
    def reset(self):
        self.board = np.zeros([3,3])
        self.moves = 0
        self.x_turn = True
        try:
            self.x_player.reset()
        except BaseException:
            pass
        try:
            self.y_player.reset()
        except BaseException:
            pass

    # returns the max and min of sum of each axis + each diagonal
    def max_min(self):
        col_sum = np.sum(self.board,0)
        row_sum = np.sum(self.board,1)
        maxs = np.maximum(col_sum,row_sum)
        mins = np.minimum(col_sum,row_sum)
        diag0 = self.board.trace(0)
        diag1 = np.flip(self.board,0).trace(0)
        return max(max(maxs), diag0, diag1), min(min(mins), diag0, diag1)

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
        while self.moves < 9:
            player = self.x_player if self.x_turn else self.o_player
            opponent = self.o_player if self.x_turn else self.x_player
            state = self.state(player)
            try:
                m = player.move(self,state)
                if self.move(m,player):
                    player.update(self,state,1)
                    opponent.update(self,state,-1)
                    break
            except ValueError:
                player.update(self,state,-10)
                break
            self.x_turn = not self.x_turn

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

