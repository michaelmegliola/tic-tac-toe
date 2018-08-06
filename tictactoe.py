import numpy as np

class BasePlayer:
    
    def __init__(self):
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
    
    def __init__(self):
        super().__init__()
        
    def move(self, game, state):
        pass

    def update(self, game, state, reward):
        pass

class RandomPlayer(BasePlayer):
    
    def __init__(self):
        super().__init__()
        
    def move(self, game, state):
        return game.sample()

    def update(self, game, state, reward):
        pass

class HumanPlayer(BasePlayer):
    
    def __init__(self):
        super().__init__()
        
    def move(self, game, state):
        print(game)
        return int(input())

    def update(self, game, state, reward):
        if reward != 0:
            print('Human player received a reward',reward)

class PrettyGoodPlayer(BasePlayer):
    
    def __init__(self):
        super().__init__()
    
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

class VeryGoodPlayer(PrettyGoodPlayer):
    def __init__(self):
        super().__init__()
    
    def move(self, game, state):
        move = self.winning_move(game)
        if move != -1:
            return move
        move = self.block_opponent(game)
        if move != -1:
            return move
        move = self.double_winner(game.board,self.n)
        if move != -1:
            return move
        move = self.double_winner(game.board,-self.n)
        if move != -1:
            return move
        return game.sample()
    
    def double_winner(self, board, n):
        for row in range(3):
            for col in range(3):
                if board[row][col] == 0:
                    board[row][col] = n
                    w_col = [1 for x in np.sum(board,0) if x == n*2]
                    w_row = [1 for x in np.sum(board,1) if x == n*2]
                    winners = int(np.sum(w_col) + np.sum(w_row))        
                    winners += (1 if board.trace(0) == n*2 else 0)
                    winners += 1 if np.flip(board,0).trace(0) == n*2 else 0
                    board[row][col] = 0
                    if winners > 1:
                        return row * 3 + col
        return -1

class MinimaxPlayer(BasePlayer):
    
    # return a valid move (0..9, equal to [row * 3 + col] )
    def move(self, game, state):
        best_row = -1
        best_col = -1
        best_score = -100
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == 0:
                    game.board[row][col] = self.n
                    score = self.minimax(game,False)
                    game.board[row][col] = 0
                    if score > best_score:
                        best_score = score
                        best_row = row
                        best_col = col
        return best_row * 3 + best_col

    # receive feedback from most recent move
    def update(self, game, state, reward):
        if reward == -1:
            print('Inconceivable!')  # how did we manage to lose, having examined every outcome?
            game.replay()
    
    # check if the board is full (implying that the game is over)
    def board_is_full(self, board):
        for row in range(3):
            for col in range(3):
                if board[row][col] == 0:
                    return False
        return True
    
    # do the work first described by Jon Von Neumann in 1928
    def minimax(self, game, isMe):    
        
        # first, check for terminal conditions...
        scores = game.max_min()
        if scores[0] == 3:
            return scores[0] * self.n       # 'x' wins...
        elif scores[1] == -3:
            return scores[1] * self.n       # 'o' wins...
        if self.board_is_full(game.board):
            return 0                        # ...and a tie is also a terminal condition.
        
        if isMe:
            best = -4
            for row in range(3):
                for col in range(3):
                    if game.board[row][col] == 0:
                        game.board[row][col] = self.n
                        best = max(best, self.minimax(game, not isMe))
                        game.board[row][col] = 0
        else:
            best = 4
            for row in range(3):
                for col in range(3):
                    if game.board[row][col] == 0:
                        game.board[row][col] = -self.n
                        best = min(best, self.minimax(game, not isMe))
                        game.board[row][col] = 0
        return best 
          
class Game:   
    def __init__(self, x_player=EmptyPlayer(), o_player=EmptyPlayer()):
        self.x_player = x_player
        self.o_player = o_player
        self.x_player.set_n(1)      
        self.o_player.set_n(-1)
        self.i = 0
        self.reset()
        
    def reset(self):
        self.board = np.zeros((3,3))
        self.x_turn = True     
        self.x_player.reset() 
        self.o_player.reset()
        self.moves = 0
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
            raise ValueError('cannot sample randomly; board is full')
        while True:
            row = np.random.randint(3)  # 0,1,2
            col = np.random.randint(3)
            if self.board[row][col] == 0:
                return row * 3 + col
    
    def sequential(self):
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == 0:
                    return row * 3 + col
        raise ValueError('cannot sample sequentially; board is full')

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
        while self.moves < 9:   
            player = self.x_player if self.x_turn else self.o_player
            opponent = self.x_player if not self.x_turn else self.o_player
            state = self.state(player, self.board)
            p_row_col = player.move(self,state)
            try:
                player_wins = self.move(p_row_col,player)
            except ValueError:
                player.update(self,state,-100)
                break
            self.states.append(self.state(self.x_player, self.board)) # supports instant replay
            if player_wins:
                player.update(self,state,1)
                opponent.update(self,state,-1)
                break
            else:
                player.update(self,state,0)
                opponent.update(self,state,0)
            self.x_turn = not self.x_turn
        if player_wins:
            self.x_player.record_outcome(player.n)
            self.o_player.record_outcome(player.n)
        else:
            self.x_player.record_outcome(0)
            self.o_player.record_outcome(0)           
        return player.n
    
    def game_over(self):
        return np.max(np.absolute(self.max_min())) == 3 or self.i >= 9
   
    def replay(self):
        print('=== REPLAY =================================')
        print(self.states)
        i = 0
        for state in self.states:
            i += 1
            print('===( ' + str(i) + ' [ state=' + str(state) + ' ] )=====================\n')
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
