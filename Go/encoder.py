
import Goban
import numpy as np

class Encoder(object):
    def __init__(self,size):
        self.board_size = size
        self.planes = 2
    def name(self):
        return 'TwoPlaneEncoder'
    def encode(self, game_state,size=9):
        X = np.zeros([1,size,size,2], dtype = int)
        for i in range(game_state._BOARDSIZE**2):
            val = game_state[i]
            (x,y) = Goban.Board.unflatten(i)
            if val == Goban.Board._BLACK:
                X[0][x][y][0] = 1
            elif val == Goban.Board._WHITE:
                X[0][x][y][1] = 1
        return X
    def num_points(self):
        return self.board_size**2
    def shape(self):
        return 1,self.board_size,self.board_size,2