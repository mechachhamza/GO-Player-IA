# -*- coding: utf-8 -*-
# Le code de myPlayer ré-utilise une partie de mon travail de l'an dernier avec Arthur Jolivet

import Goban
from playerInterface import *
import math
import time
import random as rd
# import logging

# logging.basicConfig(level=logging.DEBUG, filename="logMCTS", filemode="w",format="%(asctime)-15s %(levelname)-8s %(message)s")

class myPlayerInternalBoard(Goban.Board):
    """Improved board class to obtain new capabilities"""

    def __getitem__(self, i, j):
        return self._board[i][j]

    def nb_legal_moves_per_color(self, color):
        comp = 0
        for x in range(0, self._boardsize):
            for y in range(0, self._boardsize):
                if self.lazyTest_ValidMove(color, x, y):
                    comp += 1
        return max(1, comp)


class myPlayer(PlayerInterface):
    """Reversi AI player implementation"""

    @staticmethod
    def flipColor(color):
        """Invert the color"""
        if (color == 1):
            return 2
        elif (color == 2):
            return 1
        else:
            return None

    def __init__(self):
        """Init the player with an internal board, an horizon level and a color"""
        self._horizon = 3 # <= réglage de la profondeur d'exploration souhaitée ou du temps de recherche en secondes
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        """Retrieve the player's name"""
        return "monteCarlo"

    def getPlayerMove(self):
        """Compute and return a move"""
        if self._board.is_game_over():
            print(self.getPlayerName() + " >> Well.. I guess it's over")
            return (-1, -1)

        #################################################################################
        # Change strategy HERE

        move = self.monteCarloTime(self._horizon)

        #################################################################################

        self._board.push(move)
        print(self.getPlayerName() + " >> ", move, ", I choose Ya!")
        #(c, x, y) = move
        #assert (c == self._myColor)
        #print(self.getPlayerName() + " >> This is my current board :", self._internalBoard)
        return Goban.Board.flat_to_name(move) 

    
    def playOpponentMove(self, move):
        print("Opponent played ", move, "i.e. ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 



    

    def newGame(self, color):
        """Init colors following a new game"""
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        """Display final message following the winner"""
        if self._mycolor == winner:
            print(self.getPlayerName() + " >> Yeahh!!!")
        else:
            print(self.getPlayerName() + " >> Oh, noooo :(!!")


    ########################################################################################
    ############################# Monte Carlo Tree Search ##################################
    ########################################################################################

    def monteCarloTime(self, timeSearch):
        """Strategy implementing the Monte Carlo Tree Search algorithm with our heuristic
        and a definite time search"""

        mct = MonteCarlo(self._board, self._mycolor)
        start = time.time()
        while time.time() - start < 10:
        # for i in range (10):
            mct.treeWalk(mct._tree)

        nodeList = mct._tree._childs
        bestMove = nodeList[0]._move
        bestScore = 0
        for n in nodeList:
            if n._mu > bestScore:
                # logging.info("MOVE %s With Score %f. Time %f"%(n._move,n._mu, time.time()))
                bestScore = n._mu
                bestMove = n._move
        return bestMove




########################################################################################
########################### Structures for Monte Carlo #################################
########################################################################################

class Node:
    """class node useful for the representation of the tree of moves"""

    def __init__(self, parent, move):
        self._parent = parent
        self._move = move
        self._childs = []
        self._visited = 0
        self._successful = 0
        self._mu = -float("inf")

    def championChild(self):
        champ = self._childs[0]
        muChamp = self._mu
        for c in self._childs:
            if c._visited:
                c._mu = float(c._successful / c._visited) + math.sqrt(2*math.log2(self._visited+1)/c._visited)
            if c._mu > muChamp:
                muChamp = c._mu
                champ = c
        return champ

    def update(self, reward):
        self._visited += 1
        self._successful += reward
        # if self._parent:
            # self._mu = float(self._successful / self._visited) + math.sqrt(2*math.log2(self._parent._visited+1)/self._visited)

    def __repr__(self):
        string = "Move %s"%self._move
        return string


class MonteCarlo:
    """Monte Carlo class with tree walk and random walk methods"""

    def __init__(self, board, color):
        self._board = board
        self._tree = Node(None, None)
        self._color = color

    def generateChilds(self, node):
        if self._board.is_game_over():
            return

        possible_moves = self._board.legal_moves()
        for m in possible_moves:
            node._childs.append(Node(node, m))

    def treeWalk(self, node):
        node._visited+=1
        if node._childs != []:
            cc = node.championChild()
            self._board.push(cc._move)
            reward = self.treeWalk(cc)
        else:
            self.generateChilds(node)
            if node._childs == []:
                if self._board.is_game_over():
                    return self.get_reward()
                # self._board.push(self._board.legal_moves()[0])
                reward = self.randomWalk()
            else:
                # logging.info(node._childs)
                rd.seed(time.time())
                id = rd.randrange(len(node._childs))
                """ if rd.uniform(0,1)<.5:
                    cc = node.championChild()
                    self._board.push(cc._move)
                    reward = self.treeWalk(cc)
                else: """
                child=node._childs[id]
                self._board.push(child._move)
                child._visited+=1
                reward = self.randomWalk()
        node.update(reward)
        self._board.pop()
        return reward


    def randomWalk(self):
        count = 0

        while not self._board.is_game_over():
            rd.seed(time.time())
            legal_moves = self._board.legal_moves()
            idrand = rd.randrange(len(legal_moves))
            randomMove = legal_moves[idrand]
            self._board.push(randomMove)
            count += 1

        nbBlack, nbWhite = self._board.compute_score()
        reward = 0

        if nbWhite > nbBlack:
            reward = 1 if self._color == 2 else -1
        if nbWhite < nbBlack:
            reward = 1 if self._color == 1 else -1

        for k in range(count):
            self._board.pop()

        return reward

    def get_reward(self):
        nbBlack, nbWhite = self._board.compute_score()
        reward = 0
        if nbWhite > nbBlack:
            reward = 1 if self._color == 2 else -1
        if nbWhite < nbBlack:
            reward = 1 if self._color == 1 else -1
        return reward

import argparse


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='MCTS research code')
    parser.add_argument('--levels', action="store", required=True, type=int)
    args=parser.parse_args()
    currentnode=Goban.Board()
    player = myPlayer()
    player.newGame(Goban.Board._BLACK)
    for l in range(args.levels):
        move = player.getPlayerMove()
        currentnode.push(Goban.Board.name_to_flat(move))
        """ print("Current Node: %s"%current_node)
        action = node.parent_actions[0]
        print("level %d, Player: %d"%(l,currentnode.next_player()))
        print("Num Children: %d"%len(current_node.children))
        nums=0
        for i,c in enumerate(current_node.children):
            print(i,c)
            if c==node:
                nums=i """
        print("Move played %s"%move)
        rd.seed(time.time())
        opmove = rd.choice(currentnode.legal_moves())
        currentnode.push(opmove)
        player.playOpponentMove(Goban.Board.flat_to_name(opmove))
        
        print("--------------------------------")