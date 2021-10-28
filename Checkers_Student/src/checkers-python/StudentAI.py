from BoardClasses import Board
from BoardClasses import Move
from datetime     import timedelta
from random       import randint
from timeit       import default_timer as timer
import math
import copy

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

class StudentAI():

    # Hard coded time limit in second(s).
    # TODO: Change it 480 for submission as 480 is way too long for test runs.
    
    TIME_LIMIT = 1

    def __init__(self, col, row, p):
        
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2, 2:1}
        self.color = 2
    
    def get_move(self, move):
        
        # Keep track of time.
        timeStart = timer()
        
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
        
        moves       = self.board.get_all_possible_moves(self.color)
        index       = randint(0, len(moves) - 1)        # TODO: Remove later.
        inner_index = randint(0, len(moves[index]) - 1) # TODO: Remove later.
        move        = moves[index][inner_index]         # TODO: Remove later.
        
        # If there's only one move, then return it.
        
        # if len(moves) == 1:  # Doesn't work as moves is a list of move
        #     return moves[0]  # move objects, not moves themself.
         
        while timer() < timeStart + self.TIME_LIMIT:
            
            # TODO: Should call MCTS here.
            
            pass

        self.board.make_move(move,self.color)
        return move

# ==== MONTE-CARLO TREE SEARCH =============================================== #
    
    # TODO: REQUIRED
    def evaluate():
    
    	""" Evaluation function to decide whether to explore or exploit. """
    	
    	pass
    
    # TODO: Optional
    def load_tree():
    	
    	""" Load game tree of previous game(s). """
    	
    	pass
    
    
    # TODO: Optional
    def log_tree():
    	
    	""" Write to game tree to log for future game(s). """
    	
    	pass
    
    # TODO: REQUIRED
    # We might have to code MCTS as a class object as it will be easier to
    # manage the nodes.
    def mcts(state):
        
        pass
    
    # we do alpha-beta pruning to get rid of nodes we do not need to explore
    # FOR BOARD, WHETHER TO DEEP COPY or UNDO
    def alphaBeta(self, board, player,  alpha, beta, depth):
        # we check to see if the current state is end
        # if we reach a certain depth, we want to stop searching
        if board.is_win() in [1,2] or depth == 5:
            return state # implement the heuristic here

        # the maximizing player, which is us
        if player == self.color:
            maxNode = -math.inf
            # made deep copy but wastes space so we can change this
            for move in board.get_all_possible_moves(player):
                b = copy.deepcopy(board)
                b.make_move(move, self.color)
                node, candidate = self.alphaBeta(b, self.opponent[self.color], alpha, beta, depth + 1)
                if (node > maxNode):
                    maxNode = node
                    m = candidate
                alpha = max(alpha, node)
                if beta <= alpha:
                    break
            return maxNode, m
        else:
            minNode = math.inf 
            for move in board.get_all_possible_moves(player):
                b = copy.deepcopy(board)
                b.make_move(move, self.opponent[self.color])
                node, m = self.alphaBeta(b, self.color, alpha, beta, depth + 1)
                minNode = min(minNode, node)
                beta = min(beta, node)
                if beta <= alpha:
                    break
            return minNode, m
    
