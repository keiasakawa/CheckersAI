# ==== IMPORTS =============================================================== #

from BoardClasses    import Board, Move
from copy            import deepcopy
from multiprocessing import Pool
from os              import cpu_count
from random          import choice
from timeit          import default_timer

import math

# ==== STUDENTAI ============================================================= #

class StudentAI():
    
    def __init__(self, col, row, p):
        
        self.board    = Board(col, row, p)
        self.opponent = {1: 2, 2: 1}
        self.color    = 2
        self.board.initialize_game()
        
        self.start    = default_timer()
        self.time     = 0
        self.tree     = MCTS(self.board)
    
    
    def get_move(self, move):
        
        if len(move) == 0:
            self.color = 1
        else:
            self.tree.update(move)
            self.board.make_move(move, self.opponent[self.color])
        
        if self.time == 0:
            self.time = default_timer()
            m         = self.tree.run()
            self.time = default_timer() - self.time + 8
        else:
            m = self.tree.run(default_timer() + self.time < self.start + 480)
        
        self.board.make_move(m, self.color)
        
        return m


# ==== MONTE CARLO TREE SEARCH =============================================== #

class MCTS():
    
    def __init__(self, board):
        """
        Initialize MCTS controller.
        |
        board := (Board) board to play during simulation
        """
        self.game       = deepcopy(board)   # Board to do simulation on.
        self.curr       = Node(1)           # Root node of actual game.
        self.trav       = self.curr         # Node to traversed the tree.
        self.thrd       = cpu_count()
    
    
    def run(self, simulation = True):
        """
        Run a simulation.
        |
        simulation := (bool) do simulation or skip it
        """
        
        # Return only moves.
        moves = self.game.get_all_possible_moves(self.curr.c) 
        
        if [moves[0]] == moves and [moves[0][0]] == moves[0]:
            self.update(moves[0][0])
            return moves[0][0]

        if simulation:
            
            for i in range(self.calculate()):
                
                self.select()       # May need to be dynamic for different
                self.expand()
                self.select()
                
                p = Pool()
                o = p.map(self.simulate, range(self.thrd))
                p.close()
                p.join()
                
                self.backpropagate(sum(o))
        
        m = Move.from_str(self.getBestMove())
        
        self.update(m)

        return m
    
    def calculate(self):
        return 9600 // (self.game.row * self.game.col * self.game.p)
    
    def backpropagate(self, value):
        """
        Backpropagate by returning to parent and undoing board until current
        node is reached. Update value while doing it.
        |
        moves := (uint) number of undos
        """
        
        while self.trav != self.curr:
            self.game.undo()
            self.trav.update(value, self.thrd)
            self.trav = self.trav.p
    
    
    def expand(self):
        """
        Expand node. Should only be called when there exists no child node for
        non-terminal node.
        """
        
        for piece in self.game.get_all_possible_moves(self.trav.c):
            self.trav.add(piece)
    
    
    def select(self):
        """
        Select node to traverse to. Stop when node has no children. Prioritize
        unexplored nodes.
        """
        
        L = self.trav.moves()
        
        while L:
            
            v = -1
            
            for move in L:
                
                UCT = self.trav.l[move].uct(self.trav.c)
                
                if UCT < 0:     # Minor optimization. Break from iteration if
                    m = move    # unexplored node is reached instead of
                    break       # iterating over entire children.
                elif UCT > v:   #
                    m = move    # If there's no unexplored child, then pick
                    v = UCT     # the best one for travelling player.
            
            self.game.make_move(Move.from_str(m), self.trav.c)
            self.trav = self.trav.l[m]
            L         = self.trav.moves()
    
    
    def simulate(self, null_arg):
        """
        Simulate over unexplored node. Ends when terminal node is reached and
        backpropagate appropriate value.
        |
        null_arg := placeholder argument for multiprocessing
        """
        color = self.trav.getColor()
        count = 0
        moves = self.game.get_all_possible_moves(color)
        
        while moves != []:
            
            self.game.make_move(choice(choice(moves)), color)
            
            color  = 3 - color
            count += 1
            
            moves  = self.game.get_all_possible_moves(color)
        
        terminal_value = self.game.is_win(color)
        
        if terminal_value == 1:
            return 1
        elif terminal_value == -1:
            return 0.5
        else:
            return 0
    
    
    def getBestMove(self):
        """
        Get all available moves and pick the one with the highest win rate.
        """
        score = -2
        
        if not self.curr.moves():   # More sanity check for expand.
            self.expand()
        
        for move in self.curr.moves():
            
            WR = self.curr.l[move].uct(self.curr.c, False)
            
            if WR > score:      # Select highest WR among all possible moves.
                m     = move
                score = WR
            
        return m
    
    
    def update(self, move):
        """
        Update board with given move.
        |
        move := (Move) move to update board with
        """
        self.game.make_move(move, self.curr.c)  # Update board.
            
        if str(move) not in self.curr.moves():  # Sanity check without the need
            self.trav.add([str(move)])          # for expand.
            
        self.curr   = self.curr.l[str(move)]    # Move current node to 'move'.
        self.curr.p = None                      # Clean up unused node.
        self.trav   = self.curr                 # Update travelling node.


# ==== NODE ================================================================== #

class Node():
    
    def __init__(self, player, parent = None):
        """
        Node class for MCTS.
        |
        player := (1, 2) player number for node
        parent := (Node) parent node if it exists
        """
        self.w = 0.0    # Number of wins.
        self.s = 0      # Number of simulations.
        
        self.c = player # Respective player for node.
        self.p = parent # Parent node.
        
        self.l = {}     # Dictionary of moves children.
                        # KEY := str(Move)
                        # VAL := Node()
    
    
    def add(self, children):
        """
        Add children to node.
        |
        children := list(Move) list of move to add to children dictionary.
        """
        
        for child in children:
            self.l[str(child)] = Node(3 - self.c, self)
    
    
    def getColor(self):
        """
        Return color of node.
        """
        
        return self.c
    
    
    def moves(self):
        """
        Return all name of children.
        """
        
        return list(self.l.keys())
    
    
    def uct(self, player, p = True):
        """
        Compute UCT value and win rate with respect to the player.
        |
        player := (1, 2) player number to compute for
        p      := (bool) true to compute UCT, otherwise win rate
        """
        
        if self.s == 0: # Return -1 for unexplored node. Preferred over
            return -1   # math.inf for ease of handling.
        
        if self.p != None and self.p.s == 0:    # Sanity check for ln(x) since
            p = False                           # for x < 1, it is negative.
        
        r = self.w / self.s if player == 2 else 1 - (self.w / self.s)
        
        return r  + math.sqrt(2 * math.log(self.p.s) / self.s) if p else r
    
    
    def update(self, value, s):
        """
        Update node's value. Increment simulation and add terminal value to win.
        |
        s     := (uint)   number of simulations
        value := (ufloat) value to add to win
        """
        
        self.w += value
        self.s += s


# ==== EOF =================================================================== #
