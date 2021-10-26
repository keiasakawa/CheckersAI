from random import randint
from timeit import default_timer
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

    total_time = 0.0
    TIME_OF_TIMEOUT = 480

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
    
    def get_move(self,move):
        timeStart = default.timer() # keep track of time
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        moves = self.board.get_all_possible_moves(self.color)

            index = randint(0,len(moves)-1)
            inner_index =  randint(0,len(moves[index])-1)
            move = moves[index][inner_index]
        # if it's only one move then return it
        if len(moves) == 1:
            timeEnd = 
            return moves[0]
        while remainingTime >= 3
            # index = randint(0,len(moves)-1)
            # inner_index =  randint(0,len(moves[index])-1)
            # move = moves[index][inner_index]

        self.board.make_move(move,self.color)
        return move

    # Monte Carlo Tree Search
    def mcts(state):
     # we do alpha-beta pruning to get rid of nodes we do not need to explore
    def alphabeta(state, player,  alpha, beta):
        # we check to see if the current state is end
        if state.is_win() == 2:
            return state

        if player == 2:
            max
    
