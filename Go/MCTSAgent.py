# -*- coding: utf-8 -*-

import json
import os
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.models import model_from_json
import random
from playerInterface import *
import math
import hashlib
# import logging
import Goban 
import argparse
import time
# from copy import copy, _deepcopy_atomic, deepcopy
from encoder import Encoder


#MCTS scalar.  Larger scalar will increase exploitation, smaller will increase exploration. 
SCALAR=1/math.sqrt(2.0)

# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger('MyLogger')


class State():
    def __init__(self, board, mycolor):
        self._board = board
        self.color=mycolor
        self.num_moves = len(self._board.legal_moves())
        self.prevmove = None
    def next_state(self):
        nextmove=random.choice(self._board.legal_moves())
        # nextboard=deepcopy(self._board)#self._board.copy()
        self._board.push(nextmove)
        color = self.color#Goban.Board.flip(self.color)
        next=State(self._board,color)
        next.prevmove=nextmove
        return next
    def terminal(self):
        return self._board.is_game_over()
    def reward(self):
        if self.terminal():
            res = self._board.result()
            if res == "1-0":
                return 1 if (self.color == Goban.Board._WHITE) else 0
            if res == "0-1":
                return 0 if (self.color == Goban.Board._WHITE) else 1
            else:
                return 0
        else:
            total = self._board._nbBLACK + self._board._nbWHITE
            if self.color == Goban.Board._BLACK:
                return self._board._nbBLACK/81
            else:
                return self._board._nbWHITE/81
    def __hash__(self):
        return int(self._board._currentHash)
    def __eq__(self, value):
        return hash(self)==hash(value)
    def __repr__(self):
        s = "Stones; Black %d; White %d"%(self._board._nbBLACK,self._board._nbWHITE)
        return s


class Node():
	def __init__(self, state, parent=None):
		self.visits=1
		self.reward=0.0	
		self.state=state
		self.children=[]
		self.parent=parent
	def add_child(self,child_state):
		child=Node(child_state,self)
		self.children.append(child)
	def update(self,reward):
		self.reward+=reward
		self.visits+=1
	def fully_expanded(self):
		if len(self.children)>=self.state.num_moves:
			return True
		return False
	def __repr__(self):
		s="Node; children: %d; visits: %d; reward: %f"%(len(self.children),self.visits,self.reward)
		return s

def UCTSEARCH(budget,root,model=None):
	starttime=time.time()
	while time.time()-starttime<7.5:
		""" 
			logger.info(root) """
		front=TREEPOLICY(root)
		if model is not None:
			reward = PREDICTPOLICY(front.state,model)
		else:
			reward=DEFAULTPOLICY(front.state)
		BACKUP(front,reward)
	return BESTCHILD(root,0.1,False)

def TREEPOLICY(node):
	#a hack to force 'exploitation' where there are many options, and we may not want to fully expand first
	while node.state.terminal()==False:
		if len(node.children)==0:
			return EXPAND(node)
		elif random.uniform(0,1)<.5:
			node=BESTCHILD(node,SCALAR)
		else:
			if node.fully_expanded()==False:	
				return EXPAND(node)
			else:
				node=BESTCHILD(node,SCALAR)
	return node

def EXPAND(node):
	tried_children=[c.state.prevmove for c in node.children]
	new_state=node.state.next_state()
	while new_state.prevmove in tried_children:
		new_state._board.pop()
		new_state=node.state.next_state()
	node.add_child(new_state)
	return node.children[-1]

#current this uses the most vanilla MCTS formula it is worth experimenting with THRESHOLD ASCENT (TAGS)
def BESTCHILD(node,scalar,push=True):
	bestscore=0.0
	bestchildren=[]
	for c in node.children:
		exploit=c.reward
		explore=math.sqrt(2.0*math.log(node.visits)/float(c.visits))	
		score=exploit+scalar*explore
		if score==bestscore:
			bestchildren.append(c)
		if score>bestscore:
			bestchildren=[c]
			bestscore=score
	if len(bestchildren)==0:
		print("OOPS: no best child found, probably fatal")
	bestchild = random.choice(bestchildren)
	if push:
		node.state._board.push(bestchild.state.prevmove)
	return bestchild

def get_reward(board,color):
    if board.is_game_over():
        res = board.result()
        if res == "1-0":
            return 1 if (color == Goban.Board._WHITE) else 0
        if res == "0-1":
            return 0 if (color == Goban.Board._WHITE) else 1
        else:
            return 0
    else:
        total = board._nbBLACK + board._nbWHITE
        if color == Goban.Board._BLACK:
            return board._nbBLACK/81
        else:
            return board._nbWHITE/81

def DEFAULTPOLICY(state):
	reward = state.reward()
	board=state._board
	color=state.color
	count=0
	while board.is_game_over()==False: #and abs(reward)<0.5:
		mov = random.choice(board.legal_moves())
		board.push(mov)
		count+=1
	reward = get_reward(board,color)
	for i in range(count):
		board.pop()
	return reward

def PREDICTPOLICY(state, model):
    encod = Encoder(9)
    encoded_board = encod.encode(state._board)
    color = state.color
    return model.predict(encoded_board)[0][color-1]

def BACKUP(node,reward):
	while node.parent!=None:
		node.state._board.pop()
		node.visits+=1
		node.reward+=reward
		node=node.parent
	node.visits+=1
	node.reward+=reward
	node=node.parent
	return


class myPlayer(PlayerInterface):

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self.openings= 5
        self._turns_played = 0
        self.opening_moves = ['E5','F5','D5','E6','F6','D6','E4','F4','D4',
							'E3','F3','D3','C3','G3','E7','F7','D7','C7','G7','C6','C5','G6','G5',
							'H8','H5','H2','B8','B5','B2','E2','E8']
        jsmodel = open('../predict_model.json', 'r')
        jsmodel_load=jsmodel.read()
        self.model = tf.keras.models.model_from_json(jsmodel_load)
        self.model.load_weights("../model_weights.h5")
        self.model.compile(loss='mae', optimizer='adam', metrics=['accuracy'])

    def getPlayerName(self):
        return "MCAgent"
	
    def getOpening(self):
        legal_actions = self._board.legal_moves()
        random.seed(time.time())
        while True:
            if self._turns_played ==0:
                move = Goban.Board.name_to_flat(random.choice(self.opening_moves[:9]))
            elif self._turns_played <3:
                move = Goban.Board.name_to_flat(random.choice(self.opening_moves[:16]))
            else:
                move = Goban.Board.name_to_flat(random.choice(self.opening_moves))
            if move in legal_actions:
                break
        return move

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        # moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        if self._turns_played < self.openings:
            move = self.getOpening()
        else:
        	current_node=Node(State(self._board,self._mycolor))
        	node = UCTSEARCH(50,current_node,self.model)
        	move = node.state.prevmove
        self._turns_played+=1
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

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
	parser.add_argument('--num_sims', action="store", required=True, type=int)
	parser.add_argument('--levels', action="store", required=True, type=int)
	args=parser.parse_args()
	b=Goban.Board()
	color=Goban.Board._BLACK
	current_node=Node(State(b,color))
	player = myPlayer()
	player.newGame(Goban.Board._BLACK)
	for l in range(args.levels):
		current_node=UCTSEARCH(args.num_sims/(l+1),current_node,player.model)
		print("level %d"%l)
		print("Num Children: %d"%len(current_node.children))
		for i,c in enumerate(current_node.children):
			print(i,c)
		print("Best Child: %s"%current_node)
		
		print("--------------------------------")