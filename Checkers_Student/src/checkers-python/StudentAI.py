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
        self.time = 0
    
    
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
            if self.time == 0:
                self.time = timer()
                move = self.tree.run(800, moves)
                self.time = timer() - self.time + 8
            else:
                move =                                                      \
                self.tree.run(0                                             \
                              if timer() + self.time > self.timeStart + 480 \
                              else 800, moves)
        
        self.tree.update_current(move)
        self.board.make_move(move, self.color)
        
        return move
    

# ==== MONTE-CARLO TREE SEARCH =============================================== #

class MCTS():
    
    """
    A controller of the Monte-Carlo tree search. Responsible for handling
    necessary functions, such as back-propagation, expansion, selection, and
    simulation.
    
    Optionally, it can log and load a game save to improve future performance.
    """
    
    def __init__(self, board, player):
        
        self.curr = Node(1)
        self.trav = self.curr
        
        self.game = copy.deepcopy(board)
        self.play = player
        
    
    def run(self, q, moves):
        """ Execute the entire MCTS process q times and return optimal move. """
        
        for i in range(q):
            self.select()
            self.simulate()
        
        mval = -1
        move = str(moves[0][0])
        
        for name, leaf in self.curr.l.items():
            
            uctv = leaf.uct(self.play)
            
            if mval < uctv and uctv != math.inf:
                move = name
                mval = uctv
        
        return Move.from_str(move)
    
    
    def backpropagate(self, value):
        """ Back-propagation from terminal nodes. """
        
        while self.trav != self.curr:
            
            self.game.undo()
            
            self.trav.w += value
            self.trav.s += 1
            self.trav    = self.trav.p
        
        self.curr.w += value
        self.curr.s += 1
        
    
    def expand(self):
        """ Fill up traveled node with leaf node(s). """
        
        for piece in self.game.get_all_possible_moves(self.trav.c):
            for move in piece:
                self.trav.l[str(move)] = Node(3 - self.trav.c, self.trav)
    
    
    def select(self):
        """ Select node until a childless node is reached. """
        
        while self.trav.l:
            
            mval = 0
            move = list(self.trav.l.keys())[0]
            
            for name, leaf in self.trav.l.items():
                
                uctv = leaf.uct(self.play)
                
                if mval < uctv:
                    move = name
                    mval = uctv
            
            self.game.make_move(Move.from_str(move), self.trav.c)
            self.trav = self.trav.l[move]
    
    
    def simulate(self):
        """ Run a simulation. Should be run on a node with no child. """

        player = self.play
        while self.game.is_win(self.play) == 0:
            self.expand()
            
            if not self.trav.l:
            	break
            
            '''# REMOVE IF NECESSARY!!!!!
            eval = -math.inf
            for move in list(self.trav.l.keys()):
                self.game.make_move(Move.from_str(move), self.trav.c)
                result = self.evaluation(player)
                if result > eval:
                    final = move
                self.game.undo()'''

            # INCLUDE IF NECESSARY!!!!!
            move      = choice(list(self.trav.l.keys()))
            self.game.make_move(Move.from_str(move), self.trav.c)
            self.trav = self.trav.l[move]
            # We need to switch to the perspective of the other player
            player = 3 - player
        
        term_val = self.game.is_win(self.play)
        
        if term_val == 1:
            self.backpropagate(1)
        elif term_val == -1:
            self.backpropagate(0.5)
        else:
            self.backpropagate(0)

    # IGNORE 
    """ we do alpha-beta pruning to get rid of nodes we do not need to explore """
    def alphaBeta(self, board, player,  alpha, beta, depth):
        # we check to see if the current state is end
        # if we reach a certain depth, we want to stop searching
        if board.is_win(player) != 0 or depth == 0:
            return self.evaluation(board)

        # the maximizing player, which is us
        if player == self.play:
            maxNode = -math.inf
            breakFlag = False
            for piece in board.get_all_possible_moves(player):
                for move in piece:
                    board.make_move(move, player)
                    node = self.alphaBeta(board, 3 - player, alpha, beta, depth - 1)
                    board.undo()
                    maxNode = max(maxNode, node)
                    alpha = max(alpha, node)
                    if beta <= alpha:
                        breakFlag = True
                        break
                if breakFlag:
                    break
            return maxNode
        else:
            minNode = math.inf 
            breakFlag = False
            for piece in board.get_all_possible_moves(player):
                for move in piece:
                    board.make_move(move, player)
                    node = self.alphaBeta(board, 3 - player, alpha, beta, depth - 1)
                    board.undo()
                    minNode = min(minNode, node)
                    beta = min(beta, node)
                    if beta <= alpha:
                        breakFlag = True
                        break
                if breakFlag:
                    break
            return minNode
    
    def update_current(self, move):
        """ Update current node with move. """
        
        if not self.curr.l:
            self.expand()
        
        self.game.make_move(move, self.trav.c)
        self.curr = self.curr.l[str(move)]
        self.trav = self.curr
    
    
    def evaluation(self, player):
        """ Heuristic evaluation in selecting random node for simulation. """
        value = 0
        for row in range(self.game.row):
            for col in range(self.game.col):
                piece = self.game.board[row][col]
                # create evaluation depending on the color
                if player == 1: # BLACK
                    if (piece == 1):
                        value += 1
                        if piece.is_king:
                            value += 3
                        if col == 0 or col == self.game.col - 1:
                            value += 0.5
                    else:
                        value -= 1
                        if piece.is_king: # if it's a king it doesn't matter what row
                            value -= 3
                        if col == 0 or col == self.game.col - 1:
                            value -= 0.5
                elif player == 2: # WHITE
                    if (piece == 1):
                        value -= 1
                        if piece.is_king: # if it's a king it doesn't matter what row
                            value -= 3
                        if col == 0 or col == self.game.col - 1:
                            value -= 0.5
                    else:
                        value += 1
                        if piece.is_king: # if it's a king it doesn't matter what row
                            value += 3
                        if col == 0 or col == self.game.col - 1:
                            value += 0.5
        return value

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
                   (self.w / self.s) + (self.C * math.sqrt(math.log(self.p.s) / self.s))
        else:
            return math.inf            \
                   if self.s == 0 else \
                   1 - (self.w / self.s) + (self.C * math.sqrt(math.log(self.p.s) / self.s))

# ==== EOF =================================================================== #
