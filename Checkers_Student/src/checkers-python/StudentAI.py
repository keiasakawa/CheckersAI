from BoardClasses import Board
from BoardClasses import Move
from random       import randint
from timeit       import default_timer as timer

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

class StudentAI():

    # Keep track of time.
    timeStart = timer()

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
        
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
        
        moves       = self.board.get_all_possible_moves(self.color)
        index       = randint(0, len(moves) - 1)        # TODO: Remove later.
        inner_index = randint(0, len(moves[index]) - 1) # TODO: Remove later.
        move        = moves[index][inner_index]         # TODO: Remove later.
        
        if [moves[0]] == moves and [moves[0][0]] == [moves[0]]:
            
            # If there's only one move, then return it.
            move = moves[0][0]
            
        elif timer() + 4 > self.timeStart + 480:
            
            # Return random moves if 4 seconds or less are remaining.
            i    = randint(0, len(moves) - 1)
            move = moves[i][randint(0, len(moves[i]) - 1)]

        else:
            pass
            # TODO: Call MCTS.
            
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
    
