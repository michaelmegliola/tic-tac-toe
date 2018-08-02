import numpy as np

class BasePlayer:
    
    def __init__(self, display=False):
        self.display = display
        self.reset_metrics()
    
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
        return self.__class__.__name__ + ' w/l/t=' + str(self.wins) + '/' + str(self.losses) + '/' + str(self.ties)       

class EmptyPlayer(BasePlayer):
    
    def __init__(self,display=False):
        super().__init__(display)
        
    def move(self, game, state):
        pass

    def update(self, game, state, reward):
        pass

class RandomPlayer(BasePlayer):
    
    def __init__(self,display=False):
        super().__init__(display)
        
    def move(self, game, state):
        return game.sample()

    def update(self, game, state, reward):
        pass

class HumanPlayer(BasePlayer):
    
    def __init__(self,display=True):
        super().__init__(display)
        
    def move(self, game, state):
        return int(input())

    def update(self, game, state, reward):
        if reward != 0:
            print('Human player received a reward',reward)

class ProceduralPlayer(BasePlayer):
    
    def __init__(self,display=False):
        super().__init__(display)
    
    def move(self, game, state):
        move = self.winning_move(game)
        if move != -1:
            return move
        move = self.block_opponent(game)
        if move != -1:
            return move
        return game.sample()

    def winning_move(self, game):
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == 0:
                    game.board[row][col] = self.n
                    max_min = game.max_min()
                    game.board[row][col] = 0
                    if max_min[0] == self.n * 3 or max_min[1] == self.n * 3:
                        return row * 3 + col
        return -1

    def block_opponent(self, game):
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == 0:
                    game.board[row][col] = -self.n
                    max_min = game.max_min()
                    game.board[row][col] = 0
                    if max_min[0] == -self.n * 3 or max_min[1] == -self.n * 3:
                        return row * 3 + col
        return -1
        
    def update(self, board, state, reward):
        pass
    
    
class Game:
    
    def __init__(self, x_player=EmptyPlayer(), o_player=EmptyPlayer()):
        self.x_player = x_player
        self.o_player = o_player
        self.i = 0
        self.reset()
        
    def reset(self):
        self.board = np.zeros((3,3))
        self.moves = 0
        self.x_turn = True     
        self.x_player.reset() 
        self.o_player.reset()
        self.states = []

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

    def state(self, player, board):
        i = 0
        n = 1 if player is self.x_player else -1
        for row in range(3):
            for col in range(3):
                i += (n * board[row][col] + 1) * (3 ** (row*3+col))
        return int(i)
        
    def construct_board(state):
        board = np.zeros((3,3))
        for row in range(2,-1,-1):
            for col in range(2,-1,-1):
                exp = 3 ** (row*3+col)
                board[row][col] = state // exp - 1
                state = state % exp
        return board        

    def play(self):
        self.reset()
        self.i+=1       
        self.x_player.set_n(1)      
        self.o_player.set_n(-1)

        while self.moves < 9:
            player = self.x_player if self.x_turn else self.o_player
            opponent = self.o_player if self.x_turn else self.x_player
            state = self.state(player, self.board)
            winner = 0
            try:
                p_row_col = player.move(self,state)
                game_over = self.move(p_row_col,player)
                self.states.append(self.state(self.x_player, self.board))
                if player.display:
                    print(self)
                if game_over:
                    player.update(self,state,1)
                    opponent.update(self,state,-1)
                    winner = player.n
                    break
            except ValueError:
                if player.display:
                    print('=== ILLEGAL MOVE ===================')
                player.update(self,state,-10)
                winner = -player.n
                break
            self.x_turn = not self.x_turn
        self.x_player.record_outcome(winner)
        self.o_player.record_outcome(winner)
        return winner

    def replay(self):
        print('=== REPLAY =========================')
        print(self.states)
        i = 0
        for state in self.states:
            i += 1
            print('===( ' + str(i) + ' )============================\n')
            print(Game.draw(Game.construct_board(state)))
        print('\n')

    def draw(board):
        s = ''
        for i in range(3):
            for line in range(3):
                for j in range(3):
                    if board[i][j] == 1:
                        if line == 0:
                            s += '\\ /'
                        elif line == 1:
                            s += ' X '
                        else:
                            s += '/ \\'
                    elif board[i][j] == -1:
                        if line == 0:
                            s += 'OOO'
                        elif line == 1:
                            s += 'O O'
                        else:
                            s += 'OOO'
                    else:
                        if line == 1:
                            s += ' ' + str(int(i*3+j)) + ' '
                        else:
                            s += '   '
                    s += '   '
                s += '\n'
            s += '\n'
        return s
    
    def __str__(self):
        s = '\n---( '
        s += str(self.moves)
        s += ' )--------------------------\n\n'
        s += Game.draw(self.board)
        s += 'x state = '
        s += str(self.state(self.x_player, self.board))
        s += ', o state = '
        s += str(self.state(self.o_player, self.board))
        return s
