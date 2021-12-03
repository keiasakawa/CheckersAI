# ==== IMPORTS =============================================================== #

from BoardClasses    import Board, Move
from copy            import deepcopy
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
        self.tree     = MCTS(self.board, self.color)

    def get_move(self, move):
        
        if len(move) == 0:
            self.color = 1
            self.tree.update_color(self.color)
        else:
            self.tree.update(move)
            self.board.make_move(move, self.opponent[self.color])
        
        if self.time == 0:
            self.time = default_timer()
            m         = self.tree.run()
            self.time = default_timer() - self.time + 6
        else:
            m = self.tree.run(default_timer() + self.time < self.start + 480)
        
        self.board.make_move(m, self.color)
        
        return m



# ==== MONTE CARLO TREE SEARCH =============================================== #

class MCTS():
    
    def __init__(self, board, player):
        """
        Initialize MCTS controller.
        |
        board := (Board) board to play during simulation
        """
        self.player = player
        self.game = deepcopy(board) # Board to do simulation on.
        self.curr = Node(1)         # Root node of actual game.
        self.trav = self.curr       # Travelling node to traversed the tree.
    
    
    def run(self, simulation = True):
        """
        Run a simulation.
        |
        simulation := (bool) do simulation or skip it
        """
        # only 1 move
        moves = self.game.get_all_possible_moves(self.curr.c) 
        if [moves[0]] == moves and [moves[0][0]] == moves[0]:
            self.update(moves[0][0])
            return moves[0][0]

        if simulation:
            for i in range(1000):   # Run 'x' number of simulations.
                self.select()       # May need to be dynamic for different
                
                # WE ONLY EXPAND ONCE
                self.expand()
                self.simulate()     # game environment.
        
        m = Move.from_str(self.getBestMove())
        
        self.update(m)
        return m
    
    
    def backpropagate(self, value, count):
        """
        Backpropagate by returning to parent and undoing board until current
        node is reached. Update value while doing it.
        |
        value := (uint) value to backpropagate
        """

        # undo because we did not save these states
        while count > 0:
            self.game.undo()
            count -= 1

        while self.trav != self.curr:
            self.game.undo()

            # update since the value is going to be different for the opponent
            if self.trav.c != self.player:
                self.trav.update_opponent(value)
            else:
                self.trav.update(value)
            self.trav = self.trav.p
    
    
    def expand(self):
        """
        Expand node. Should only be called when there exists no child node for
        non-terminal node.
        """
        
        for piece in self.game.get_all_possible_moves(self.trav.c):
            self.trav.add(piece)

        # We Make A Random Move
        if self.trav.l:
            m = choice(self.trav.moves())
            self.game.make_move(Move.from_str(m), self.trav.c)
            self.trav = self.trav.l[m]
    
    
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
    
    
    def simulate(self):
        """
        Simulate over unexplored node. Ends when terminal node is reached and
        backpropagate appropriate value.
        """
        player = self.trav.c
        terminal_value = self.game.get_all_possible_moves(player)
        count = 0
        while len(terminal_value) != 0 :
            
            '''
            s = default_timer()
            if not self.trav.moves():   # Sanity check for expand.
                self.expand()
            f.write("Expand: " + str(default_timer() - s))
            f.write("\n")
            moves = self.trav.moves()
            
            if not moves: break # Break when there's no available move.
            '''
            piece = choice(terminal_value)
            m              = choice(piece)
            
            # s = default_timer()
            self.game.make_move(m, player)
            player = 3 - player
            # f.write("Make Move: " + str(default_timer() - s))
            # f.write("\n")
            #self.trav      = self.trav.l[str(m)]
            #s = default_timer()
            terminal_value = self.game.get_all_possible_moves(player)
            #f.write("Win: " + str(default_timer() - s))
            #f.write("\n")
            count += 1

        terminal_value = self.game.is_win(player)
        #f.write("Simulate: " + str(default_timer() - start))
        #f.write("\n")
        #f.write("Count: " + str(count))
        #f.write("\n")
        #f.close()

        # we need to back propagate on what color we are, not player 1
        if terminal_value == self.player:
            self.backpropagate(1, count)
        elif terminal_value == -1:
            self.backpropagate(0.5, count)
        else:
            self.backpropagate(0, count)
    
    
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
    
    def update_color(self, color):
        self.player = color

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
    
    
    def __repr__(self):
        """
        Return formatted Node to standard output. USE FOR DEBUGGING.
        """
        
        return self.str()
    
    
    def add(self, children):
        """
        Add children to node.
        |
        children := list(Move) list of move to add to children dictionary.
        """
        
        for child in children:
            self.l[str(child)] = Node(3 - self.c, self)
    
    
    def moves(self):
        """
        Return all name of children.
        """
        
        return list(self.l.keys())
    
    
    def str(self, name = "", d = 0):
        """
        Handles formatting node to a string. USE FOR DEBUGGING.
        |
        name := (str)  name of node
        d    := (uint) depth of node
        """
        
        out = " " * d + name + \
              "," + str(self.w) + "," + str(self.s) + "," + str(self.c)
        
        for child in self.moves():
            out += "\n" + self.l[child].str(child, d + 1)
        
        return out
    
    
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


    def update(self, value):
        """
        Update node's value. Increment simulation and add terminal value to win.
        |
        value := (ufloat) value to add to win
        """
        
        self.w += value
        self.s += 1

    def update_opponent(self, value):
        if value == 0:
            self.w += 1
        elif value == 0.5:
            self.w += 0.5
        self.s += 1

# ==== EOF =================================================================== #
