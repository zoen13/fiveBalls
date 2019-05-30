import sys, pygame, random
import pygame.gfxdraw
from pygame.locals import *

pygame.init()
# pygame游戏窗口大小
WINDOWWIDTH = 700 
WINDOWHEIGHT = 450

#格子大小
BOXSIZE = 50

#圆球半径
BALLSIZE = 20

#棋盘格行列数
BOARDWIDTH = 9
BOARDHEIGHT = 9

#               R    G    B
GRAY        = (100, 100, 100)
NAVYBLUE    = ( 60,  60, 100)
WHITE       = (255, 255, 255)
RED         = (255,   0,   0)
GREEN       = (  0, 255,   0)
BLUE        = (  0,   0, 255)
YELLOW      = (255, 255,   0)
ORANGE      = (255, 128,   0)
PURPLE      = (255,   0, 255)
CYAN        = (  0, 255, 255)
BLACK       = (  0,   0,   0)
BRIGHTBLUE  = (  0,  50, 255)

#圆球颜色列表
BALLCOLORLIST = [BRIGHTBLUE, RED, GREEN, YELLOW, ORANGE, PURPLE, CYAN]

#设置初始得分
score = 0

#游戏窗口背景
bg = GRAY

#字体
FONT = pygame.font.Font('freesansbold.ttf', 18)
BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption("五子连珠")

def main():
    screen.fill(bg)
        
    #绘制网格线
    for bx in range(BOARDWIDTH+1):
        pygame.draw.line(screen,BLACK,(0,bx*BOXSIZE),(BOARDWIDTH*BOXSIZE,bx*BOXSIZE),1)
    for by in range(BOARDHEIGHT+1):
        pygame.draw.line(screen,BLACK,(by*BOXSIZE,0),(by*BOXSIZE,BOARDWIDTH*BOXSIZE),1)
    
    #绘制Next文字
    nextSurf = FONT.render('Next:', True, YELLOW, bg)
    nextRect = nextSurf.get_rect()
    nextRect.topright = (WINDOWWIDTH - 180, 20)
    screen.blit(nextSurf, nextRect)
    
    #绘制Score文字
    scoreSurf = FONT.render('Score:', True, YELLOW, bg)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topright = (WINDOWWIDTH - 180, 120)
    screen.blit(scoreSurf, scoreRect)

    #绘制Restart按钮
    width = 2 #width参数是绘制外边缘的粗细。 如果width为零，则填充矩形。
    pos = WINDOWWIDTH - 180, WINDOWHEIGHT - 100, 100, 60 #参数意义，x轴坐标，Y轴坐标，x长度，Y长度
    pygame.draw.rect(screen, YELLOW, pos, width)

    #绘制Restart文字
    restartSurf = FONT.render('Restart', True, YELLOW, bg)
    restartRect = restartSurf.get_rect()
    restartRect.topright = (WINDOWWIDTH - 100, WINDOWHEIGHT - 80)
    screen.blit(restartSurf, restartRect)

    #建立主数组，用灰色初始化
    board = [[GRAY]* BOARDWIDTH for _ in range(BOARDHEIGHT)]
    nextArr = genNext()
    fillByNext(board, nextArr)
    drawBoard(board)
    nextArr = genNext()
    #设置初始得分
    drawScore(0)

    #两次点击的格子信息
    firstClick = "something"
    secondClick = "something"
    firstX = -1
    secondX = -1
    firstY = -1
    secondY = -1

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == MOUSEBUTTONUP:
                # Handle mouse click events
                mousex, mousey = event.pos
                movexy = getSpaceClicked(mousex, mousey)
                if mousex <= BOARDWIDTH * BOXSIZE and mousey <= BOARDHEIGHT * BOXSIZE:
                    if hasBall(board, movexy[0], movexy[1]):
                        firstClick = "BALL"
                        firstX = movexy[0]
                        firstY = movexy[1]
                        secondClick = "something"
                        secondX = -1
                        secondY = -1
                    else:
                        if firstClick == "BALL":
                            secondClick = "BLANK"
                            secondX = movexy[0]
                            secondY = movexy[1]

                    if firstClick == "BALL" and secondClick == "BLANK":
                        if havePath(board,firstX,firstY,secondX,secondY):
                            moveBall(board, firstX, firstY, secondX, secondY)
                            if not find5(board, secondX, secondY):
                                fillByNext(board, nextArr)
                                drawBoard(board)
                                nextArr = genNext()
                            firstClick = "something"
                            secondClick = "something"
                            firstX = -1
                            secondX = -1
                            firstY = -1
                            secondY = -1
                
                # 响应restart按钮
                if mousex <= 620 and mousey <= 410 and mousex >= 520 and mousey >= 350:
                    main()
        pygame.display.flip()
        #pygame.display.update()
        #pygame.time.delay(10)

#判断点击是否落在格子中
def getSpaceClicked(mousex, mousey):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mousex >= x * BOXSIZE and \
               mousex <= (x + 1) * BOXSIZE and \
               mousey >= y * BOXSIZE and \
               mousey <= (y + 1) * BOXSIZE:
               return (x, y)
    return None

#将nextArr数组中的圆球随机填充到board数组中空位中去(灰色)
def fillByNext(board, nextArr):
    emptyArr = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == GRAY:
                emptyArr.append((x,y))       
    random.shuffle(emptyArr)
    if len(emptyArr) < len(nextArr):
        return False
    else:
        for n in range(len(nextArr)):
            board[emptyArr[n][0]][emptyArr[n][1]]=nextArr[n]
            find5(board,emptyArr[n][0],emptyArr[n][1])

#根据参数绘制圆球
def drawBall(x,y,color):
    # pygame.gfxdraw.aacircle(screen, x, y, BALLSIZE, color)
    # pygame.gfxdraw.filled_circle(screen, x, y, BALLSIZE, color)
    pygame.draw.circle(screen, color, (x, y), BALLSIZE) 

#绘制主数组
def drawBoard(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBall(BOXSIZE*x+int(BOXSIZE*0.5), BOXSIZE*y+int(BOXSIZE*0.5), board[x][y])

#建立Next数组，绘制Next三个圆球
def genNext():
    nextArr = []
    for _ in range(3):
        nextColor = random.choice(BALLCOLORLIST)
        nextArr.append(nextColor)
        drawBall(525 + _*50, 75, nextColor)
    return nextArr

def drawScore(score):
    defenSurf = FONT.render(str(score), True, YELLOW, bg)
    defenRect = defenSurf.get_rect()
    defenRect.topright = (WINDOWWIDTH - 120, 120)
    screen.blit(defenSurf, defenRect)

#移动一个圆球
def moveBall(board, x1, y1, x2, y2):
    board[x2][y2] = board[x1][y1]
    drawBall(BOXSIZE*x2+int(BOXSIZE*0.5), BOXSIZE*y2+int(BOXSIZE*0.5),board[x2][y2])
    board[x1][y1] = GRAY
    drawBall(BOXSIZE*x1+int(BOXSIZE*0.5), BOXSIZE*y1+int(BOXSIZE*0.5),board[x1][y1])

#判断当前点击的格子中是否有圆球
def hasBall(board, x, y):
    if board[x][y] != GRAY:
        return True
    else:
        return False

#判断一个格子是否超越数组下标
def isValidGrid(x,y):
    if x<0 or x>=BOARDWIDTH or y<0 or y>=BOARDHEIGHT:
        return False
    else:
        return True

#找到五子连珠
def find5(board, x, y):
    line1 = [(x,y)]
    line2 = [(x,y)]
    line3 = [(x,y)]
    line4 = [(x,y)]

    a1 = x
    b1 = y
    while isValidGrid(a1+1,b1):
        if board[a1+1][b1] == board[x][y]:
            line1.append((a1+1,b1))
            a1 = a1+1
        else:
            a1 = -100
    a2 = x
    b2 = y
    while isValidGrid(a2-1,b2):
        if board[a2-1][b2] == board[x][y]:
            line1.append((a2-1,b2))
            a2 = a2-1
        else:
            a2 = -100
    a3 = x
    b3 = y
    while isValidGrid(a3+1,b3-1):
        if board[a3+1][b3-1] == board[x][y]:
            line2.append((a3+1,b3-1))
            a3 = a3+1
            b3 = b3-1
        else:
            a3 = -100
    a4 = x
    b4 = y
    while isValidGrid(a4-1,b4+1):
        if board[a4-1][b4+1] == board[x][y]:
            line2.append((a4-1,b4+1))
            a4 = a4-1
            b4 = b4+1
        else:
            a4 = -100
    a5 = x
    b5 = y
    while isValidGrid(a5,b5-1):
        if board[a5][b5-1] == board[x][y]:
            line3.append((a5,b5-1))
            b5 = b5-1
        else:
            a5 = -1
    a6 = x
    b6 = y
    while isValidGrid(a6,b6+1):
        if board[a6][b6+1] == board[x][y]:
            line3.append((a6,b6+1))
            b6 = b6+1
        else:
            a6 = -100
    a7 = x
    b7 = y
    while isValidGrid(a7-1,b7-1):
        if board[a7-1][b7-1] == board[x][y]:
            line4.append((a7-1,b7-1))
            a7 = a7-1
            b7 = b7-1
        else:
            a7 = -100
    a8 = x
    b8 = y
    while isValidGrid(a8+1,b8+1):
        if board[a8+1][b8+1] == board[x][y]:
            line4.append((a8+1,b8+1))
            a8 = a8+1
            b8 = b8+1
        else:
            a8 = -100
    
    if len(line1) >= 5:
        erase(board,line1)
    if len(line2) >= 5:
        erase(board,line2)
    if len(line3) >= 5:
        erase(board,line3)
    if len(line4) >= 5:
        erase(board,line4)
    if len(line1) >= 5 or len(line2) >= 5 or len(line3) >= 5 or len(line4) >= 5:
        return True
    else:
        return False

#清除五子连珠
def erase(board,line):
    for l in line:
        board[l[0]][l[1]] = GRAY
        drawBall(BOXSIZE*l[0]+int(BOXSIZE*0.5), BOXSIZE*l[1]+int(BOXSIZE*0.5),board[l[0]][l[1]])
    global score
    score += len(line)*(len(line)-3)
    drawScore(score)

#找邻居
def findNeighbour(board,x,y):
    neighbour = []
    if isValidGrid(x+1,y) and board[x+1][y] == GRAY:
        neighbour.append((x+1,y))
    if isValidGrid(x-1,y) and board[x-1][y] == GRAY:
        neighbour.append((x-1,y))
    if isValidGrid(x,y+1) and board[x][y+1] == GRAY:
        neighbour.append((x,y+1))
    if isValidGrid(x,y-1) and board[x][y-1] == GRAY:
        neighbour.append((x,y-1))
    return neighbour

#找两个点之间是否有路径
def havePath(board, x, y, tx, ty):
    oNeighbour = [(x,y)]
    nNeighbour = findNeighbour(board,x,y) + oNeighbour

    while len(oNeighbour) < len(nNeighbour):
        if (tx, ty) in nNeighbour:
            return  True
        else:
            oNeighbour = nNeighbour
            tNeighbour = []
            nNeighbour = []

            for o in oNeighbour:
                tNeighbour += findNeighbour(board,o[0],o[1])

            tNeighbour += [(x,y)]
            for t in tNeighbour:
                if t not in nNeighbour:
                    nNeighbour.append(t)
    return False

if __name__ == '__main__':
    main()