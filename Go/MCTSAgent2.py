import numpy as np
from collections import defaultdict
import Goban
import argparse
from playerInterface import *
import random
import time
# import logging

# logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="w",format="%(asctime)-15s %(levelname)-8s %(message)s")

class MonteCarloTreeSearchNode():
    """ state: For our game it represents the board state. Generally the board state is represented by an array. For normal Tic Tac Toe, it is a 3 by 3 array.
        parent: It is None for the root node and for other nodes it is equal to the node it is derived from. For the first turn as you have seen from the game it is None.
        children: It contains all possible actions from the current node. For the second turn in our game this is 9 or 8 depending on where you make your move.
        parent_action: None for the root node and for other nodes it is equal to the action which it’s parent carried out.
        _number_of_visits: Number of times current node is visited
        results: It’s a dictionary
        _untried_actions: Represents the list of all possible actions
        action: Move which has to be carried out. 
    """
    def __init__(self, state: Goban.Board, parent=None, parent_action=[]):
        self.state = state
        self.parent = parent
        self.parent_actions = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        self.color=None
        self.timer = 5
        self.needs_to_move =len(self.parent_actions)
        return
    
    def untried_actions(self):
        self._untried_actions = self.state.legal_moves()
        return self._untried_actions
    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses
    
    def n(self):
        return self._number_of_visits
    
    def expand(self):
        action = self._untried_actions.pop()
        # next_state = self.move(action)
        actions = self.parent_actions.copy()
        actions.append(action)
        child_node = MonteCarloTreeSearchNode(
            self.state, self, self.parent_actions + [action])

        self.children.append(child_node)
        return child_node
    
    def is_terminal_node(self):
        return self.state.is_game_over()
    
    def rollout(self):
        moved = 0
        for i in range(self.needs_to_move):
            if self.parent_actions[moved] in self.state.legal_moves()  and (not self.state.is_game_over()):
                self.state.push(self.parent_actions[moved])
                moved+=1
        
        current_rollout_state = self.state
        cout=0
        while not current_rollout_state.is_game_over():
            possible_moves = current_rollout_state.legal_moves()
            action = self.rollout_policy(possible_moves)
            current_rollout_state.push(action)
            cout+=1
        
        res = current_rollout_state.result()
        
        for i in range(cout):
            current_rollout_state.pop()

        for j in range(moved):
            self.state.pop()
        
        return self.get_result(res)

    def get_result(self, res):
        Player = self.color
        if res == "1-0":
            return 1 if (Player == Goban.Board._WHITE) else -1
        if res == "0-1":
            return -1 if (Player == Goban.Board._WHITE) else 1
        else:
            return 0

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)
    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def best_child(self, c_param=0.1):
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        random.seed(time.time())
        return possible_moves[np.random.randint(len(possible_moves))]
    
    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node():
            if len(current_node.children)==0:
                return current_node.expand()
            elif random.uniform(0,1)<.5:
                current_node = current_node.best_child()
            else:
                if not current_node.is_fully_expanded():
                    return current_node.expand()
                else:
                    current_node = current_node.best_child()
        return current_node

    def best_action(self,color):
        self.color=color
        simulation_no = 50
        starttime = time.time()
        while time.time()-starttime <= self.timer:
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        return self.best_child(c_param=0.1)

    def get_legal_actions(self): 
        return self.state.legal_moves()
    
    def is_game_over(self):
        return self.state.is_game_over()
    
    def game_result(self):
        '''
        Modify according to the game or 
        needs. Returns 1 or 0 or -1 depending
        on your state corresponding to win,
        tie or a loss.
        '''
        Player = self.color
        res = self.state.result()
        if res == "1-0":
            return 1 if (Player == Goban.Board._WHITE) else -1
        if res == "0-1":
            return -1 if (Player == Goban.Board._WHITE) else 1
        else:
            return 0

    def move(self,action):
        '''
        Modify according to the game or 
        needs. Changes the state of the 
        board with a new value. Returns 
        the new state after making a move.
        '''
        # nextboard = deepcopy(self.state)
        # nextboard.push(action)
        return #nextboard

    def __repr__(self):
        s1 = "Stones; Black %d; White %d"%(self.state._nbBLACK,self.state._nbWHITE)
        s2 = " Node; children: %d; visits: %d; reward: "%(len(self.children),self._number_of_visits)
        s3 = "{}".format(self.q())
        return s1+s2+s3

class myPlayer(PlayerInterface):

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._turns_played = 0
        self.openings = 5
        self.opening_list = []
        # self.log_file=open("Logs.log","w")

    def getPlayerName(self):
        return "MCAgent"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        # moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        if self._turns_played < self.openings:
            move = self.playOpening()
        else:
            current_node=MonteCarloTreeSearchNode(self._board)
            node = current_node.best_action(self._mycolor)
            move = node.parent_actions[0]

        self._turns_played+=1
        if not self._board.push(move):
            return self.getPlayerMove()

        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        # logging.info("%d: I am Playing %s"%(self._turns_played,Goban.Board.flat_to_name(move)))
        # logging.info("Stones: Black %d, White %d"%(self._board._nbBLACK, self._board._nbWHITE))
        # self._board.prettyPrint()
        return Goban.Board.flat_to_name(move) 

    def playOpening(self):
        legal_moves = self._board.legal_moves()
        center = 'E5'
        flatcenter = Goban.Board.name_to_flat(center)
        if self._turns_played==0 and not (flatcenter in legal_moves):
            return flatcenter
        else:
            return random.choice(legal_moves)

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
           # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")





if __name__=="__main__":
    parser = argparse.ArgumentParser(description='MCTS research code')
    parser.add_argument('--levels', action="store", required=True, type=int)
    args=parser.parse_args()
    currentnode=Goban.Board()
    for l in range(args.levels):
        current_node=MonteCarloTreeSearchNode(currentnode)
        print("Current Node: %s"%current_node)
        node=current_node.best_action(Goban.Board._BLACK)
        print("Current Node after: %s"%current_node)
        action = node.parent_actions[0]
        print("level %d, Player: %d"%(l,currentnode.next_player()))
        print("Num Children: %d"%len(current_node.children))
        nums=0
        for i,c in enumerate(current_node.children):
            print(i,c)
            if c==node:
                nums=i
        print("Best Child: %d, %s"%(nums,node))
        print("Move played %s"%Goban.Board.flat_to_name(action))
        currentnode.push(action)
        currentnode.push(random.choice(currentnode.legal_moves()))
        print("--------------------------------")