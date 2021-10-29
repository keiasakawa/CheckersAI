from BoardClasses import Board
from BoardClasses import Move
from random       import randint
from timeit       import default_timer as timer

import math
import copy

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

C = math.sqrt(2)    # Exploration constant.

class MCTS():
    
    def __init__(self, board, root = None, state = None):
        
        self.b = board      # Keep board state of node.
        
        self.w = 0          # Count the number of win(s).
        self.s = 0          # Count the number of simulation(s).
        
        self.root = root    # Keep track of parent for back-propagation.
        self.leaf = []      # List of childrens to explore or exploit.
        
        # TODO: Implement state for specialized action.
        
    # DONE
    def backpropagate(self, value):
        """  Propagate terminal value recursively back to descendant nodes. """
        
        self.w += value
        self.s += 1
        
        self.root.backpropagate(value)
        
    
    # TODO: REQUIRED
    def expansion(self):
        """ Fill current node with children. """
        
        self.leaf = 
    
    
    # TODO: Optional
    def evaluation(self):
        """ Heuristic evaluation in selecting random node for simulation. """
        
        pass
    
    
    # TODO: REQUIRED    
    def selection(self, depth):
        """ Select a child node to explore based on UCT value. """
        
        pass
    
    
    # TODO: REQUIRED
    def simulation(self):
        """ Simulate a game is played. """
        
        pass
    
    
    # DONE
    def uct(self):
        """ Compute the UCT value of the node for selection process. """
        
        return self.w / self.s + C * math.sqrt(math.log(self.root.v) / self.v) \
               if self.s != 0 else 1
               
    
