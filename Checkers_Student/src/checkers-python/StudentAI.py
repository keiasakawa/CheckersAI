# ==== IMPORTS =============================================================== #

from BoardClasses    import Board, Move
from copy            import deepcopy
from multiprocessing import Process, cpu_count
from random          import choice, randint
from timeit          import default_timer

import math

# ==== STUDENTAI ============================================================= #

class StudentAI():
    
    # Keep track of when the game started.
    timeStart = default_timer()
    
    def __init__(self, col, row, p):
        
        self.col      = col
        self.row      = row
        self.p        = p
        self.board    = Board(col, row, p)
        self.color    = ''
        self.opponent = {1:2, 2:1}
        self.color    = 2
        self.board.initialize_game()
        
        self.tree = MCTS(self.board, self.color, cpu_count())
        self.time = 0
    
    
    def get_move(self, move):
        
        if len(move) == 0:
            self.color = 1
            self.tree  = MCTS(self.board, self.color, cpu_count())
        else:
            self.tree.update(move)
            self.board.make_move(move, self.opponent[self.color])
        
        if self.time == 0:
            self.time = default_timer()
            move      = self.tree.run()
            self.time = default_timer() - self.time + 8
        else:
            move = self.tree.run(False)                                       \
                   if default_timer() + self.time > self.timeStart + 480 else \
                   self.tree.run()
        
        self.board.make_move(move, self.color)
        
        return move
    
    
# ==== MONTE CARLO TREE SEARCH =============================================== #

class MCTS():
    
    def __init__(self, board, player, thread = 1):
        """
        A controller of the Monte-Carlo tree search. Responsible for handling
        necessary functions, such as back-propagation, expansion, selection, and
        simulation.
        |
        board  := the current board state (Board)
        player := the player the AI is playing as (1, 2)
        thread := number of threads to allocate (uint)
        """
        
        self.curr = Node(1)    # Initialize node for first player.
        
        self.game = [deepcopy(board) for _ in range(thread)]
        self.trav = [self.curr       for _ in range(thread)]
        
        # Get number of moves to make.
        self.move = round(128000 / (board.row * board.col * board.p))
        
        self.thrd = thread  # Get number of threads.
        self.play = player  # Player's color.
    
    
    def run(self, s = True):
        """
        Run a simulation.
        |
        s := simulation (bool)
        """
        
        # Generate all possible moves.
        moves = self.game[0].get_all_possible_moves(self.play)
        
        # Return only move.
        if [moves[0]] == moves and [moves[0][0]] == [moves[0]]:
            self.update(moves[0][0])
            return moves[0][0]
        
        # Ignore spawning if running out of time.
        if s:
            
            P = []  # Collections of threads to join at the end.
            
            # Start threads.
            for i in range(self.thrd):
                p = Process(target = self.unit, args = (i, ))
                p.start()
                P.append(p)
        
            # Join threads.
            for p in P:
                p.join()
        
        v = 0                   # Base UCT value.
        m = str(moves[0][0])    # Base move.
        
        for name, leaf in self.curr.l.items():
            
            # Generate UCT without parent's weight.
            uctv = leaf.uct(self.play, False)
            
            # Select highest non-infinite value
            if v < uctv and uctv != math.inf:
                v = uctv
                m = name
        
        m = Move.from_str(m)
        
        # Update game boards.
        
        self.update(m)
        
        return m
    
    
    def unit(self, t):
        """
        Spawn a thread unit.
        |
        t := associated thread (uint)
        """
        
        for _ in range(self.move):
            self.select(t)
            self.simulate(t)
        
    def backpropagate(self, value, t):
        """
        Back-propagate from terminal nodes to current node.
        |
        value := value to back-propagate (uint)
        t     := associated thread for the back-propagation (uint)
        """
        
        # Stops when the travelled node reach the current node. While iterating,
        # undo the associated game board, back-propagate the value, and move
        # travelled node to its parent.
        while self.trav[t] != self.curr:
            
            self.game[t].undo()
            
            self.trav[t].w += value
            self.trav[t]    = self.trav[t].p
    
        
    def expand(self, t = 0):
        """
        Expand argument node.
        |
        t := associated thread for the node (uint)
        """
        
        # Expand the node by iterating all possible moves.
        for piece in self.game[t].get_all_possible_moves(self.trav[t].c):
            for move in piece:
                self.trav[t].l[str(move)] = \
                    Node(3 - self.trav[t].c, self.trav[t])
    
    
    def select(self, t):
        """
        Select a node until a childless node is reached. Update simulation
        value of selected node.
        |
        t := associated thread for the node (uint)
        """
        
        # Continue while there exists a child node.
        while self.trav[t].l:
            
            # Update the simulation value.
            self.trav[t].s += 1
            
            L = list(self.trav[t].l.keys())	# List of moves.
            v = 0                               # Initialize highest value as 0.
            m = L[0]  				# Select first move as base.
            
            for move in L:
                
                # Compute UCT value of child node.
                uctv = self.trav[t].l[move].uct(self.trav[t].c)
                
                # Select highest UCT value child.
                if v < uctv:
                    
                    v = uctv
                    m = move
                    
                    # Stop iterating after reaching unexplored node.
                    if v == math.inf:
                    	break
            
            # Move to highest UCT value child.
            self.game[t].make_move(Move.from_str(m), self.trav[t].c)
            self.trav[t] = self.trav[t].l[m]
    
    
    def simulate(self, t):
        """
        Run a simulation. Should only be called by 'unit'.
        |
        t := associated thread for the node (uint)
        """
        
        self.trav[t].s += 1
        
        # Stop only when terminal node is reached.
        while self.game[t].is_win(self.trav[t].c) == 0:
            
            self.expand(t)
            
            # Break from loop if no child spawn from expand.
            if not self.trav[t].l:
                break
            
            # Randomly move to a child node.
            move         = choice(list(self.trav[t].l.keys()))
            self.game[t].make_move(Move.from_str(move), self.trav[t].c)
            self.trav[t] = self.trav[t].l[move]
            self.trav[t].s += 1
        
        v = self.game[t].is_win(self.trav[t].c) # Compute terminal value.
        
        # Back-propagate with respective terminal value.
        if v == 1:
            self.backpropagate(1, t)
        elif v == -1:
            self.backpropagate(0.5, t)
        else:
            self.backpropagate(0, t)
    
    
    def update(self, move):
        """
        Update current node with the move.
        |
        move := move to act on board (Move)
        """
        
        # Expand current node if it's empty.
        if not self.curr.l:
            self.expand()
        
        self.curr   = self.curr.l[str(move)]
        self.curr.p = None
        
        for i in range(self.thrd):
            self.game[i].make_move(move, self.trav[i].c)
            self.trav[i] = self.curr
    
    """
    We do alpha-beta pruning to get rid of nodes we do not need to explore.
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
    """
    
    """
    def evaluation(self, player):
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
    """

# ==== NODE ================================================================== #

class Node():
    
    C = math.sqrt(2)    # Parent's weight constant.
    
    def __init__(self, player, parent = None):
        """
        A node class that tracks of possible moves and their value.
        |
        player := player that is able to make a move for associated node (1, 2)
        parent := parent node (Node)
        """
        
        self.w = 0  # Number of wins.
        self.s = 0  # Number of simulations.
        
        self.c = player # Make sure the correct player is making the move.
                        # 1 for Player 1 / Black
                        # 2 for Player 2 / White
        
        self.p = parent # Link parent for back-propagation.
        self.l = {}     # Dictionary of all possible Move objects.
                        # KEY: Move in string (ex. '(0,0)-(2,2)-(0,4)')
                        # VAL: Node associated with the key Move
    
    
    def uct(self, player, p = True):
        """
        Compute the upper confidence bound with ability to ignore the parent's
        weight.
        |
        player := player that UCT is calculated with respect to (1, 2)
        p      := include weight of parent in UCT calculation (bool)
        """
        
        # Return infinity when Node is not explored to encourage exploration.
        if self.s == 0:
            return math.inf
        
        # Compute base weight.
        w = (self.w / self.s) if player == 1 else 1 - (self.w / self.s)
        
        # Return with parent weight if True, otherwise base weight.
        return w + self.C * math.sqrt(math.log(self.p.s) / self.s) if p else w
    

# ==== EOF =================================================================== #
