# -*- coding: utf-8 -*-
"""
* Heuristic is a CNN model.
* For further information on this subject,
* refer to https://livebook.manning.com/book/deep-learning-and-the-game-of-go/chapter-6/78
"""

import json
import os
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.models import model_from_json
import time
import Goban
from random import choice, sample
from playerInterface import *
import numpy as np
from encoder import Encoder


def brute_heuristic(board: Goban.Board, mycolor):
    black_score= 0
    white_score=0
    score = board.compute_score()
    black_score = score[0]
    white_score = score[1]
    diff = black_score - white_score
    if mycolor==Goban.Board._BLACK:
        return diff
    else:
        return -diff
        
## If we want to look for faster wins
def final_score(board: Goban.Board, mycolor):
    if board.is_game_over():
        res = board.result()
        if res == "1-0":
            return 1000 if (mycolor == Goban.Board._WHITE) else -1000
        if res == "0-1":
            return -1000 if (mycolor == Goban.Board._WHITE) else 1000
        else:
            return 0
    return 0



class myPlayer(PlayerInterface):

    def __init__(self,depth=2,heuri=brute_heuristic):
        self._board = Goban.Board()
        self._mycolor = None
        self.depth=depth
        self.heuristic=heuri
        self._near_end = 40 # variation of number of turns
        self._end = 60 # as to change the depth if the game is near the end
        self._timeout = 0 # timeout 5 seconds
        self.totaltime = 8*60 # total play time: 8 minutes
        self._turns_played = 0
        self._times = []
        ## Loading model from a file
        jsmodel = open('model-final.json', 'r')
        jsmodel_load=jsmodel.read()
        self.model = tf.keras.models.model_from_json(jsmodel_load)
        self.model.load_weights("model-TP-IA.h5")
        self.model.compile(loss='mae', optimizer='adam', metrics=['accuracy'])

    def getPlayerName(self):
        return "AlphaBeta Player"

    def predict_heuristic(self,board: Goban.Board, color):
        if self._turns_played<1:
            return self.heuristic(board,color)
        encod = Encoder(9)
        encoded_board = encod.encode(board)
        if self.model is not None:
            return self.model.predict(encoded_board)[0][self._mycolor-1]*100
        return self.heuristic(board, self._mycolor)

    def getPlayerMove(self, moves_to_consider=20):
        if self._board.is_game_over() :
            print("Referee told me to play but the game is over!")
            return "PASS" 
        
        if self.totaltime<=1:
            legal_actions = self._board.legal_moves()
            move = choice(legal_actions)
            self._board.push(move)
            return Goban.Board.flat_to_name(move)

        self._moves_to_consider = moves_to_consider
        if self._end>=self._turns_played>=self._near_end:
            self.depth=2
        elif self._turns_played>=self._end:
            self.depth=3
        
        if len(self._board.legal_moves()) >= 20:
            self.depth=2

        Alpha = float("-inf")
        Beta = float("inf")

        self._timeout=time.time()
        val, moves = self.MaxAlpha(Alpha, Beta, self.depth)
        endtime=time.time() - self._timeout
        self.totaltime-=endtime
        self._times.append(endtime)
        self._timeout=5
        move = moves[0]
        self._board.push(move)
        self._turns_played+=1
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        return Goban.Board.flat_to_name(move) 

    def MaxAlpha(self,alpha,beta,depth):
        if self._board.is_game_over():
            return final_score(self._board,self._mycolor), []
        # self._board.is_game_over() or 
        if depth==0 or time.time()-self._timeout>7.5:
            return self.predict_heuristic(self._board, self._mycolor), []
        
        best_eval=alpha
        best_moves = []


        legal_moves = self._board.legal_moves()
        if self._moves_to_consider and len(legal_moves) > self._moves_to_consider:
            legal_moves = sample(legal_moves, self._moves_to_consider)

        for move in legal_moves:
            self._board.push(move)
            val, moves = self.MinBeta(alpha, beta, depth)
            self._board.pop()
            alpha = max(alpha, val)
            if val > best_eval:
                best_eval=val
                best_moves=[move] + moves
            if best_eval >= beta:
                return best_eval, best_moves
        return best_eval, best_moves
            
    def MinBeta(self, alpha, beta, depth):
        if self._board.is_game_over():
            return final_score(self._board,self._mycolor), []
        # self._board.is_game_over() or 
        if depth==0 or time.time()-self._timeout>7.5:
            return self.predict_heuristic(self._board, self._mycolor), []
        
        worst_=beta
        worst_moves=[]

        legal_moves = self._board.legal_moves()
        if self._moves_to_consider and len(legal_moves) > self._moves_to_consider:
            legal_moves = sample(legal_moves, self._moves_to_consider)

        for move in self._board.legal_moves():
            self._board.push(move)
            val, moves = self.MaxAlpha(alpha,beta,depth-1)
            self._board.pop()
            beta = min(beta, val)
            if val < worst_:
                worst_=val
                worst_moves=[move]+moves
            if worst_ <= alpha:
                return worst_, worst_moves
        return worst_, worst_moves

        

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