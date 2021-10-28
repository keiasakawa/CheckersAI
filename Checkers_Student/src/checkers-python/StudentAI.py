from BoardClasses import Board
from BoardClasses import Move
from datetime     import timedelta
from random       import randint
from timeit       import default_timer as timer

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
    
    def alphabeta(state, player, alpha, beta):
        # we check to see if the current state is end
        if state.is_win() == 2:
            return state

        if player == 2:
            max
    
