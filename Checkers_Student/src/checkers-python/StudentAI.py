from BoardClasses import Board
from BoardClasses import Move
from random       import choice
from random       import randint
from timeit       import default_timer as timer

import copy
import math
import os

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
        self.tree = MCTS(self.board, self.color)
    
    def get_move(self, move):
        
        if len(move) != 0:
            self.tree.update_current(move)
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
            self.tree = MCTS(self.board, self.color)
        
        moves = self.board.get_all_possible_moves(self.color)
        
        if [moves[0]] == moves and [moves[0][0]] == [moves[0]]:
            move = moves[0][0]
        else:
            move = \
            self.tree.run(0                                          \
                          if timer() + 4 > self.timeStart + 480 else \
                          100, moves)
        
        self.tree.update_current(move)
        self.board.make_move(move, self.color)
        
        if self.board.is_win(self.color) != 0:
            self.tree.log()
        
        return move
    
    """ we do alpha-beta pruning to get rid of nodes we do not need to explore """
    # FOR BOARD, WHETHER TO DEEP COPY or UNDO
    def alphaBeta(self, board, player,  alpha, beta, depth):
        # we check to see if the current state is end
        # if we reach a certain depth, we want to stop searching
        if board.is_win() in [1,2] or depth == 5:
            return  # implement the heuristic here

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

# ==== MONTE-CARLO TREE SEARCH =============================================== #

class MCTS():
    
    """
    A controller of the Monte-Carlo tree search. Responsible for handling
    necessary functions, such as back-propagation, expansion, selection, and
    simulation.
    
    Optionally, it can log and load a game save to improve future performance.
    """
    
    def __init__(self, board, player):
        
        self.root = Node(1)
        self.curr = self.root
        self.trav = self.root
        
        self.game = copy.deepcopy(board)
        self.play = player
        
        if os.path.exists(str(self.game.col) + "_" + \
                          str(self.game.row) + "_" + \
                          str(self.game.p)):
            self.load()
    
    # TODO: Complete. Require testing.
    def run(self, q, moves):
        """ Execute the entire MCTS process q times and return optimal move. """
        
        for i in range(q):
            self.select()
            self.simulate()
        
        mval = -1
        move = str(moves[0][0])
        
        for name, leaf in self.curr.l.items():
            
            uctv = leaf.uct(self.play)
            
            if mval < uctv:
                move = name
                mval = uctv
        
        return Move.from_str(move)
    
        
    # TODO: Complete. Require testing.
    def backpropagate(self, value):
        """ Back-propagation from terminal nodes. """
        
        s = True
        
        while self.trav != self.root:
            
            if self.trav == self.curr:
                s = False
            
            if s:
                self.game.undo()
            
            self.trav.w += value
            self.trav.s += 1
            self.trav    = self.trav.p
        
        self.root.w += value
        self.root.s += 1
        
        self.trav = self.curr
        
    
    # TODO: Complete. Require testing.
    def expand(self):
        """ Fill up traveled node with leaf node(s). """
        
        for piece in self.game.get_all_possible_moves(self.trav.c):
            for move in piece:
                self.trav.l[str(move)] = Node(3 - self.trav.c, self.trav)
    
    
    # TODO: Complete. Require testing.
    def select(self):
        """ Select node until a childless node is reached. """
        
        while self.trav.l:
            
            mval = 0
            
            for name, leaf in self.trav.l.items():
                
                uctv = leaf.uct(self.play)
                
                if mval < uctv:
                    move = name
                    mval = uctv
            
            self.game.make_move(Move.from_str(move), self.trav.c)
            self.trav = self.trav.l[move]
    
    
    # TODO: Complete. Require testing.
    def simulate(self):
        """ Run a simulation. Should be run on a node with no child. """
        
        while self.game.is_win(self.play) == 0:
            self.expand()
            
            if not self.trav.l:
            	break
            
            move      = choice(list(self.trav.l.keys()))
            self.game.make_move(Move.from_str(move), self.trav.c)
            self.trav = self.trav.l[move]
        
        term_val = self.game.is_win(self.play)
        
        if term_val == 1:
            self.backpropagate(1)
        elif term_val == -1:
            self.backpropagate(0.5)
        else:
            self.backpropagate(0)
    
    
    # TODO: Complete. Require testing.
    def update_current(self, move):
        """ Update current node with move. """
        
        if not self.curr.l:
            self.expand()
        
        self.game.make_move(move, self.trav.c)
        self.curr = self.curr.l[str(move)]
        self.trav = self.curr
    
    
    # TODO: OPTIONAL. Incomplete.
    def load(self):
        """ Log the game into a file. """
        
        f = open(str(self.game.col) + "_" + \
                 str(self.game.row) + "_" + \
                 str(self.game.p), "w")
        
    
    
    # TODO: Complete.
    def log(self):
        """ Load a previous log if it exists. """
        
        f = open(str(self.game.col) + "_" + \
                 str(self.game.row) + "_" + \
                 str(self.game.p), "w")
        
        output_str = self.parse("", self.root) + self.dfs(self.root, 1)
        
        f.write(output_str)
        f.close()
    
    
    # TODO: Complete.
    def dfs(self, node, lvl):
        """ Depth-first search for logging. """
        
        output_str = ""
        
        for name, leaf in node.l.items():
            output_str += " " * lvl +             \
                          self.parse(name, leaf) + \
                          self.dfs(leaf, lvl + 1)
        
        return output_str
    
    
    # TODO: Complete.
    def parse(self, name, node):
        """ Parse node to string for logging. """
        
        return name + "," + str(node.w) + "," + str(node.s) + "\n"
    
#   def evaluation(self):
#       """ Heuristic evaluation in selecting random node for simulation. """
#       value = 0
#       for row in self.b:
#           for col in self.b[row]:
#               piece = self.b[row][col]
#               if piece.color == self.player: # change
#                   value += 1
#                   if piece.is_king:
#                       value += 1
#                   else:
#                       value += row # farther up = better
#                   if col == 0 or col == self.b.col - 1:
#                       value += 0.5
#               elif piece.color == self.opponent[self.player]:
#                   value -= 1
#                   if piece.is_king: # if it's a king it doesn't matter what row
#                       value -= 1
#                   else:
#                       value -= self.b.row - row
#                   if col == 0 or col == self.b.col - 1:
#                       value -= 0.5
#       return value

# ==== NODE ================================================================== #

class Node():
    
    C = math.sqrt(2)
    
    def __init__(self, player, parent = None):
        
        self.w = 0      # Number of win(s).
        self.s = 0      # Number of simulation(s).
        
        self.c = player # Make sure the correct player is making the move.
                        # 1 for Player 1 / Black
                        # 2 for Player 2 / White
        
        self.p = parent # Pin parent node for back-propagation.
        self.l = {}     # Dictionary of all possible Move object(s).
                        # KEY: Move in string (ex. '(0,0)-(2,2)-(0,4)')
                        # VALUE: The node associated with the move
    
    
    def uct(self, player):
        """ Compute the upper confidence bound. """
        
        if player == 1:
            return math.inf            \
                   if self.s == 0 else \
                   (self.w / self.s) + (self.C * math.log(self.p.s / self.s))
        else:
            return math.inf            \
                   if self.s == 0 else \
                   1 - (self.w / self.s) + (self.C * math.log(self.p.s / self.s))

# ==== EOF =================================================================== #
