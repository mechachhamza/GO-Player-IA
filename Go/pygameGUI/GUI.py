import pygame
from Goban import *
import sys
import time
from io import StringIO

"""
This file is the GUI on top of the game backend.
"""

BACKGROUND = 'Background.jpg'
BOARD_SIZE = (820, 820)
BLACK = (0, 0, 0)
RECT_SIZE=90
GO_SIZE=9


def get_rbg(color):
    if color == 2:
        return 255, 255, 255
    elif color == 1:
        return 0, 0, 0
    else:
        return 0, 133, 211

def get_relative_coords(point):
    return point[0],GO_SIZE-point[1]-1

def coords(point):
    """Return the coordinate of a stone drawn on board"""
    return 45 + point[0] * RECT_SIZE, 45 + point[1] * RECT_SIZE


def leftup_corner(point):
    return -15 + point[0] * RECT_SIZE, -15 + point[1] * RECT_SIZE


class UI:
    def __init__(self):
        """Create, initialize and draw an empty board."""
        self.outline = pygame.Rect(45, 45, 720, 720)
        self.screen = None
        self.background = None
        self._board = Board()
        self.exit_outline = pygame.Rect(720, 5, 60, 30)

    def initialize(self):
        """This method should only be called once, when initializing the board."""
        # This method is from https://github.com/eagleflo/goban/blob/master/goban.py
        pygame.init()
        pygame.display.set_caption('Go board')
        self.screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
        self.background = pygame.image.load(BACKGROUND).convert()
        smallfont = pygame.font.SysFont('Corbel',35)
        text = smallfont.render('Game is in session' , True , BLACK)
        pygame.draw.rect(self.background, BLACK, self.outline, 3)
        # Outline is inflated here for future use as a collidebox for the mouse
        self.outline.inflate_ip(20, 20)
        for i in range(8):
            for j in range(8):
                rect = pygame.Rect(45 + (RECT_SIZE * i), 45 + (RECT_SIZE * j), RECT_SIZE, RECT_SIZE)
                pygame.draw.rect(self.background, BLACK, rect, 1)
        for i in range(2):
            for j in range(2):
                coords = (45+RECT_SIZE*2 + (RECT_SIZE*4 * i), 45+RECT_SIZE*2 + (RECT_SIZE*4 * j))
                pygame.draw.circle(self.background, BLACK, coords, 5, 0)
        
        
        pygame.draw.rect(self.background, BLACK, self.exit_outline)
        self.exit_outline.inflate_ip(20,20)
        ex = smallfont.render('EXIT' , True , (255,255,255))

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(text , (45,5))
        self.screen.blit(ex, (720,5))
        pygame.display.update()

    def draw(self, point, color, size=20):
        color = get_rbg(color)
        pygame.draw.circle(self.screen, color, coords(get_relative_coords(point)), size, 0)
        pygame.display.update()

    def remove(self, point):
        blit_coords = leftup_corner(get_relative_coords(point))
        area_rect = pygame.Rect(blit_coords, (90, 90))
        self.screen.blit(self.background, blit_coords, area_rect)
        pygame.display.update()


    def display_result(self,result):
        print('Dispaying Results -->{}'.format(result))
        smallfont = pygame.font.SysFont('Corbel',35)
        text = 'Results: ' + result
        myresult = smallfont.render(text , True , BLACK)
        pygame.draw.rect(self.background, BLACK, self.outline, 3)
        self.screen.blit(myresult , (400,5))

    def capture(self,fc):
        string = self._board._breadthSearchString(fc)
        for s in string:
            coords = Board.unflatten(s)
            self.remove(coords)
            # self._board[s]


    def play_move(self,fcoord):
        if self._board._gameOver: return
        if fcoord != -1:  # pass otherwise
            alreadySeen, tmpHash = self._board._is_super_ko(fcoord, self._board._nextPlayer)
            if alreadySeen: 
                self._board._historyMoveNames.append(self._board.flat_to_name(fcoord))
                return False
            captured = self._board._put_stone(fcoord, self._board._nextPlayer)

            # captured is the list of Strings that have 0 liberties
            for fc in captured:
                self._board._capture_string(fc)
                self.capture(fc)

            assert tmpHash == self._board._currentHash
            self._board._lastPlayerHasPassed = False
            if self._board._nextPlayer == self._board._WHITE:
                self._board._nbWHITE += 1
            else:
                self._board._nbBLACK += 1
        else:
            if self._board._lastPlayerHasPassed:
                self._board._gameOver = True
            else:
                self._board._lastPlayerHasPassed = True
            self._board._currentHash ^= self._board._passHashB if self._board._nextPlayer == Board._BLACK else self._board._passHashW

        self._board._seenHashes.add(self._board._currentHash)
        self._board._historyMoveNames.append(self._board.flat_to_name(fcoord))
        self._board._nextPlayer = Board.flip(self._board._nextPlayer)
        return True

    def draw_board(self,move):
        self.play_move(Board.name_to_flat(move))

        self.draw(Board.name_to_coord(move), self._board[Board.name_to_flat(move)])
        self.check_events()
        if self._board.is_game_over():
            result = self._board.result()
            result += ',Go Score :' + self._board.final_go_score()
            self.display_result(result)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.exit_outline.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                    break

    def save_image(self, path_to_save):
        pygame.image.save(self.screen, path_to_save)


""" ui = UI()
ui.initialize()

ui.draw_board('A1')
ui.draw_board('A2')
ui.draw_board('A3')
ui.draw_board('A4')
ui.draw_board('A5')
ui.draw_board('A6')
ui.draw_board('A7')
ui.draw_board('A8')

while True:
    pygame.time.wait(100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            break
         """


''' Sorry no comments :).
'''
import importlib
import time
from io import StringIO

def fileorpackage(name):
    if name.endswith(".py"):
        return name[:-3]
    return name

if len(sys.argv) > 2:
    classNames = [fileorpackage(sys.argv[1]), fileorpackage(sys.argv[2])]
elif len(sys.argv) > 1:
    classNames = [fileorpackage(sys.argv[1]), 'myPlayer']
else:
    classNames = ['myPlayer', 'myPlayer']

b = Board()

players = []
player1class = importlib.import_module(classNames[0])
player1 = player1class.myPlayer()
player1.newGame(Board._BLACK)
players.append(player1)

player2class = importlib.import_module(classNames[1])
player2 = player2class.myPlayer()
player2.newGame(Board._WHITE)
players.append(player2)

ui = UI()
ui.initialize()

totalTime = [0,0] # total real time for each player
nextplayer = 0
nextplayercolor = Board._BLACK
nbmoves = 1

outputs = ["",""]
sysstdout= sys.stdout
stringio = StringIO()
wrongmovefrom = 0

while not b.is_game_over():
    print("Referee Board:")
    b.prettyPrint() 
    print("Before move", nbmoves)
    legals = b.legal_moves() # legal moves are given as internal (flat) coordinates, not A1, A2, ...
    print("Legal Moves: ", [b.move_to_str(m) for m in legals]) # I have to use this wrapper if I want to print them
    nbmoves += 1
    otherplayer = (nextplayer + 1) % 2
    othercolor = Board.flip(nextplayercolor)
    
    currentTime = time.time()
    sys.stdout = stringio
    move = players[nextplayer].getPlayerMove() # The move must be given by "A1", ... "J8" string coordinates (not as an internal move)
    sys.stdout = sysstdout
    playeroutput = stringio.getvalue()
    stringio.truncate(0)
    stringio.seek(0)
    print(("[Player "+str(nextplayer) + "] ").join(playeroutput.splitlines(True)))
    outputs[nextplayer] += playeroutput
    totalTime[nextplayer] += time.time() - currentTime
    print("Player ", nextplayercolor, players[nextplayer].getPlayerName(), "plays: " + move) #changed 

    if not Board.name_to_flat(move) in legals:
        print(otherplayer, nextplayer, nextplayercolor)
        print("Problem: illegal move")
        wrongmovefrom = nextplayercolor
        break
    b.push(Board.name_to_flat(move)) # Here I have to internally flatten the move to be able to check it.
    ui.draw_board(move)

    players[otherplayer].playOpponentMove(move)
 
    nextplayer = otherplayer
    nextplayercolor = othercolor

print("The game is over")
b.prettyPrint()
result = b.result()
print("Time:", totalTime)
print("GO Score:", b.final_go_score())
print("Winner: ", end="")
if wrongmovefrom > 0:
    if wrongmovefrom == b._WHITE:
        print("BLACK")
    elif wrongmovefrom == b._BLACK:
        print("WHITE")
    else:
        print("ERROR")
elif result == "1-0":
    print("WHITE")
elif result == "0-1":
    print("BLACK")
else:
    print("DEUCE")

while True:
    pygame.time.wait(100)
    """ for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            break """
    ui.check_events()