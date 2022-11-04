import tkinter as tk
import turtle
import random
from tkinter import messagebox
import math
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
  # Themes: blue (default), dark-blue, green


global move_history

def MakeEmptyBoard(size):
    board = []
    for i in range(size):
        board.append([" "]*size)
    # print("boardsize:", len(board[0]))
    return board

def CheckIsEmpty(board):
    return board == [[' ']*len(board)]*len(board)

def CheckIsIn(board, y, x):
    return 0 <= y < len(board) and 0 <= x < len(board)

def DrawStone(x,y,colturtle):
    colturtle.goto(x,y-0.3)
    colturtle.pendown()
    colturtle.begin_fill()
    colturtle.circle(0.3)
    colturtle.end_fill()
    colturtle.penup()

def CheckOutOfBounds(move, N, M):
    if move[0] >= N or move[0] < 0 or move[1] >= M or move[1] < 0:
        return True
    return False

def March(board,y,x,dy,dx,length):
    '''
    tìm vị trí xa nhất trong dy,dx trong khoảng length

    '''
    yf = y + length*dy 
    xf = x + length*dx
    # chừng nào yf,xf không có trong board
    while not CheckIsIn(board, yf,xf):
        yf -= dy
        xf -= dx
        
    return yf,xf

def FindPossibleMove(board):  
    '''
    khởi tạo danh sách tọa độ có thể có tại danh giới các nơi đã đánh phạm vi 3 đơn vị
    '''
    #mảng taken lưu giá trị của người chơi và của máy trên bàn cờ
    taken = []
    # mảng directions lưu hướng đi (8 hướng)
    directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,-1),(-1,1),(1,-1)]
    # cord: lưu các vị trí không đi 
    cord = {}
    
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != ' ':
                taken.append((i,j))
    ''' duyệt trong hướng đi và mảng giá trị trên bàn cờ của người chơi và máy, kiểm tra nước không thể đi(trùng với 
    nước đã có trên bàn cờ)
    '''
    for direction in directions:
        dy,dx = direction
        for coord in taken:
            y,x = coord
            for length in [1,2,3,4]:
                move = March(board,y,x,dy,dx,length)
                if move not in taken and move not in cord:
                    cord[move]=False
    return cord

def ReturnScoreOfList(lis,col):
    
    blank = lis.count(' ')
    filled = lis.count(col)
    
    if blank + filled < 5:
        return -1
    elif blank == 5:
        return 0
    else:
        return filled

def ChangeRowToList(board,y,x,dy,dx,yf,xf):
    '''
    trả về list của y,x từ yf,xf
    
    '''
    row = []
    while y != yf + dy or x !=xf + dx:
        row.append(board[y][x])
        y += dy
        x += dx
    return row

def ReturnScoreOfRow(board,cordi,dy,dx,cordf,col):
    '''
    trả về một list với mỗi phần tử đại diện cho số điểm của 5 khối

    '''
    colscores = []
    y,x = cordi
    yf,xf = cordf
    row = ChangeRowToList(board,y,x,dy,dx,yf,xf)
    for start in range(len(row)-4):
        score = ReturnScoreOfList(row[start:start+5],col)
        colscores.append(score)
    
    return colscores

def ReturnScoreReady(scorecol):
    '''
    Khởi tạo hệ thống điểm

    '''
    sumcol = {0: {},1: {},2: {},3: {},4: {},5: {},-1: {}}
    for key in scorecol:
        for score in scorecol[key]:
            if key in sumcol[score]:
                sumcol[score][key] += 1
            else:
                sumcol[score][key] = 1
            
    return sumcol

def ReturnScoreOfCol(board,col):
    '''
    tính toán điểm số mỗi hướng của column dùng cho is_win;
    '''

    f = len(board)
    #scores của 4 hướng đi
    scores = {(0,1):[],(-1,1):[],(1,0):[],(1,1):[]}
    for start in range(len(board)):
        scores[(0,1)].extend(ReturnScoreOfRow(board,(start, 0), 0, 1,(start,f-1), col))
        scores[(1,0)].extend(ReturnScoreOfRow(board,(0, start), 1, 0,(f-1,start), col))
        scores[(1,1)].extend(ReturnScoreOfRow(board,(start, 0), 1,1,(f-1,f-1-start), col))
        scores[(-1,1)].extend(ReturnScoreOfRow(board,(start,0), -1, 1,(0,start), col))
        
        if start + 1 < len(board):
            scores[(1,1)].extend(ReturnScoreOfRow(board,(0, start+1), 1, 1,(f-2-start,f-1), col)) 
            scores[(-1,1)].extend(ReturnScoreOfRow(board,(f -1 , start + 1), -1,1,(start+1,f-1), col))
            
    return ReturnScoreReady(scores)

def ReturnScoreOfColOne(board,col,y,x):
    '''
    trả lại điểm số của column trong y,x theo 4 hướng,
    key: điểm số khối đơn vị đó -> chỉ ktra 5 khối thay vì toàn bộ
    '''
    
    scores = {(0,1):[],(-1,1):[],(1,0):[],(1,1):[]}
    
    scores[(0,1)].extend(ReturnScoreOfRow(board,March(board,y,x,0,-1,4), 0, 1,March(board,y,x,0,1,4), col))
    
    scores[(1,0)].extend(ReturnScoreOfRow(board,March(board,y,x,-1,0,4), 1, 0,March(board,y,x,1,0,4), col))
    
    scores[(1,1)].extend(ReturnScoreOfRow(board,March(board,y,x,-1,-1,4), 1, 1,March(board,y,x,1,1,4), col))

    scores[(-1,1)].extend(ReturnScoreOfRow(board,March(board,y,x,-1,1,4), 1,-1,March(board,y,x,1,-1,4), col))
    
    return ReturnScoreReady(scores)

def CheckTF34score(score3,score4):
    '''
    trả lại trường hợp chắc chắn có thể thắng(4 ô liên tiếp)
    '''
    for key4 in score4:
        if score4[key4] >=1:
            for key3 in score3:
                if key3 != key4 and score3[key3] >=2:
                        return True
    return False

def CheckWinningSituation(sumcol):
    '''
    trả lại tình huống chiến thắng dạng như:
    {0: {}, 1: {(0, 1): 4, (-1, 1): 3, (1, 0): 4, (1, 1): 4}, 2: {}, 3: {}, 4: {}, 5: {}, -1: {}}
    1-5 lưu điểm có độ nguy hiểm từ thấp đến cao,
    -1 là rơi vào trạng thái tồi, cần phòng thủ
    '''
    
    if 1 in sumcol[5].values():
        return 5
    elif len(sumcol[4])>=2 or (len(sumcol[4])>=1 and max(sumcol[4].values())>=2):
        return 4
    elif CheckTF34score(sumcol[3],sumcol[4]):
        return 4
    else:
        score3 = sorted(sumcol[3].values(),reverse = True)
        if len(score3) >= 2 and score3[0] >= score3[1] >= 2:
            return 3
    return 0

def SumColValue(sumcol):
    '''
    hợp nhất điểm của mỗi hướng
    '''
    
    for key in sumcol:
        if key == 5:
            sumcol[5] = int(1 in sumcol[5].values())
        else:
            sumcol[key] = sum(sumcol[key].values())

def DoStupidScore(board,col,anticol,y,x):
    '''
    cố gắng di chuyển y,x
    trả về điểm số tượng trưng lợi thế 
    '''
    
    global colors
    M = 1000
    res,adv, dis = 0, 0, 0
    
    #tấn công
    board[y][x]=col
    #draw_stone(x,y,colors[col])
    sumcol = ReturnScoreOfColOne(board,col,y,x)       
    a = CheckWinningSituation(sumcol)
    adv += a * M
    SumColValue(sumcol)
    #{0: 0, 1: 15, 2: 0, 3: 0, 4: 0, 5: 0, -1: 0}
    adv +=  sumcol[-1] + sumcol[1] + 4*sumcol[2] + 8*sumcol[3] + 16*sumcol[4]
    
    #phòng thủ
    board[y][x]=anticol
    sumanticol = ReturnScoreOfColOne(board,anticol,y,x)  
    d = CheckWinningSituation(sumanticol)
    dis += d * (M-100)
    SumColValue(sumanticol)
    dis += sumanticol[-1] + sumanticol[1] + 4*sumanticol[2] + 8*sumanticol[3] + 16*sumanticol[4]

    res = adv + dis
    
    board[y][x]=' '
    return res

def DoBestMove(board,col):
    '''
    trả lại điểm số của mảng trong lợi thế của từng màu
    '''
    if col == 'w':
        anticol = 'b'
    else:
        anticol = 'w'
        
    movecol = (0,0)
    maxscorecol = ''
    # kiểm tra nếu bàn cờ rỗng thì cho vị trí random nếu không thì đưa ra giá trị trên bàn cờ nên đi 
    if CheckIsEmpty(board):
        movecol = ( int((len(board))*random.random()),int((len(board[0]))*random.random()))
    else:
        moves = FindPossibleMove(board)

        for move in moves:
            y,x = move
            if maxscorecol == '':
                scorecol=DoStupidScore(board,col,anticol,y,x)
                maxscorecol = scorecol
                movecol = move
            else:
                scorecol=DoStupidScore(board,col,anticol,y,x)
                if scorecol > maxscorecol:
                    maxscorecol = scorecol
                    movecol = move
    return movecol

def CheckCandidateMove(board, move, N, M, border_max_size):
    # if move is unavailable
    if board[move[0]][move[1]] != " ":
        return False
    # look for checker in size 2 proximity matrix
    for border_size in range(1, border_max_size):
        # vertical search
        for i in range(move[0] - border_size, move[0] + border_size + 1):
            for direction in [-1, 1]:
                if not CheckOutOfBounds((i, move[1] + direction * border_size), N, M):
                    if board[i][move[1] + direction * border_size] != " ":
                        return True
        # horizontal search
        for j in range(move[1] - border_size + 1, move[1] + border_size):
            for direction in [-1, 1]:
                if not CheckOutOfBounds((move[0] + direction * border_size, j), N, M):
                    if board[move[0] + direction * border_size][j] != " ":
                        return True
    # False if no checker was found in 2-proximity
    return False

def GetAllCandidateMoves(board, N, M, border_max_size):
    all_moves = []
    for i in range(N):
        for j in range(M):
            if CheckCandidateMove(board, (i, j), N, M, border_max_size):
                # print(i, j)
                all_moves.append([i, j])
    return all_moves

def CheckIsWin(board):
    
    black = ReturnScoreOfCol(board,'b')
    white = ReturnScoreOfCol(board,'w')
    
    SumColValue(black)
    SumColValue(white)
    
    if 5 in black and black[5] == 1:
        return 'Black won'
    elif 5 in white and white[5] == 1:
        return 'White won'
        
    if sum(black.values()) == black[-1] and sum(white.values()) == white[-1] or FindPossibleMove(board)==[]:
        return 'Draw'
        
    return 'Continue playing'

def UseWeakHeuristic(N, M):
    moves = GetAllCandidateMoves(board, N, M, 2)
    # print(moves)
    if moves == []:
        for i in range(N):
            for j in range(M):
                moves.append([i, j])
    j = random.randint(0, len(moves) - 1)
    return moves[j]


def ClickLevel3(x = 0,y = 0):
    global board,colors,win, move_history, size, num_click
    num_click += 1
    
    # x,y = getindexposition(x,y)
    # randommove or weak_heursitic
    x, y = UseWeakHeuristic(size, size)
    # print(x, y)
    
    if x == -1 and y == -1 and len(move_history) != 0:
        x, y = move_history[-1]
     
        del(move_history[-1])
        board[x][y] = " "
        x, y = move_history[-1]
       
        del(move_history[-1])
        board[x][y] = " "
        return
    
    if not CheckIsIn(board, x, y):
        return
    
    if board[x][y] == ' ':
        
        DrawStone(x,y,colors['b'])
        board[x][y]='b'
        
        move_history.append((x, y))
        
        game_res = CheckIsWin(board)
        if game_res in ["White won", "Black won", "Draw"]:
            # print (game_res)
            win = True
            messagebox.showinfo("Result", game_res + f" in {num_click} moves")
            ResetBoard()
            
            
        ax,ay = DoBestMove(board,'w')
        DrawStone(ax,ay,colors['w'])
        board[ax][ay]='w'    
            
        move_history.append((ax, ay))
        
        game_res = CheckIsWin(board)
        if game_res in ["White won", "Black won", "Draw"]:
            # print (game_res)
            win = True
            messagebox.showinfo("Result", game_res + f" in {num_click} moves")
            ResetBoard()

def PlayLevel3():
    global screen, board, size, num_click, label_level
    label_level.configure(text="VS: Level 3") 
    num_click = 0
    board = MakeEmptyBoard(size)
    screen.onclick(ClickLevel3)

def ResetBoard(sizeBoard=15):
    global win,board,screen,colors, move_history,size, label_level
    label_level.configure(text="Choose a level")
    turtle.clearscreen()

    size = sizeBoard
    
    move_history = []
    win = False
    board = MakeEmptyBoard(size)

    screen.bgcolor('orange')
    screen.tracer(500)

    colors = {'w':turtle.Turtle(),'b':turtle.Turtle(), 'g':turtle.Turtle()}
    colors['w'].color('white')
    colors['b'].color('black')

    for key in colors:
        colors[key].ht()
        colors[key].penup()
        colors[key].speed(0)

    border = turtle.Turtle()
    border.speed(9)
    border.penup()

    side = (size-1)/2
    i=-1
    for start in range(size):
        border.goto(start,side + side *i)    
        border.pendown()
        i*=-1
        border.goto(start,side + side *i)     
        border.penup()
        
    i=1
    for start in range(size):
        border.goto(side + side *i,start)
        border.pendown()
        i *= -1
        border.goto(side + side *i,start)
        border.penup()
        
    border.ht()


def DoComputerMove1():
    global board, size
    comp_move = GetMinimaxMove1(board, N=size, M=size, depth=1, turn='w')
    # board[comp_move[1][0]][comp_move[1][1]] = 'w'
    return (comp_move[1][0],comp_move[1][1])

def CheckGameOver(board, turn, win_streak, N, M):
    # line
    for i in range(N):
        current_length = 0
        for j in range(M):
            if board[i][j] == turn:
                current_length += 1
                if current_length == win_streak:
                    return True
            else:
                current_length = 0
    # column
    for j in range(N):
        current_length = 0
        for i in range(M):
            if board[i][j] == turn:
                current_length += 1
                if current_length == win_streak:
                    return True
            else:
                current_length = 0

    for j in range(N):
        i = 0
        l = -1
        current_length_length = 0
        while (i + l + 1 < N and j + l + 1 < N):
            l += 1
            if board[i + l][j + l] == turn:
                current_length_length += 1
                if current_length_length == win_streak:
                    return True

            else:
                current_length_length = 0
    for i in range(N):
        j = 0
        l = -1
        current_length_length = 0
        while i + l + 1 < N and j + l + 1 < N:
            l += 1
            if board[i + l][j + l] == turn:
                current_length_length += 1
                if current_length_length == win_streak:
                    return True

            else:
                current_length_length = 0

    for j in range(N):
        i = 0
        l = 0
        current_length_length = 0
        while i + l < N and j - l < N:

            if board[i + l][j - l] == turn:
                current_length_length += 1
                if current_length_length == win_streak:
                    return True
            else:
                current_length_length = 0
            l += 1

    for i in range(N):
        j = 3
        l = 0
        current_length_length = 0
        while i + l < N and j - l < N:
            if board[i + l][j - l] == turn:
                current_length_length += 1
                if current_length_length == win_streak:
                    return True
            else:
                current_length_length = 0
            l += 1
    return False

def GetStreakState(board, N, M, move, streak_len, direction, turn):
    opponent_count = 0
    i = move[0]
    j = move[1]

    if 0 <= j < M and 0 <= i < N:
        # if there is opponent checker at streak end -> increase count
        if (board[i][j] == 'b' and turn == 'w') or (board[i][j] == 'w' and turn == 'b'):
            opponent_count += 1
    # if streak end on board margin
    else:
        opponent_count += 1

    if direction == "left":
        if j - streak_len - 1 >= 0:
            # check if there is opponent checker at streak beginning -> increase count
            if (board[i][j - streak_len - 1]  == 'b' and turn == 'w') or (board[i][j - streak_len - 1]  == 'w' and turn == 'b'):
                opponent_count += 1
        else:  # if streak starts on board margin
            opponent_count += 1

    if direction == "up":
        if i - streak_len - 1 >= 0:
            if (board[i - streak_len - 1][j] == 'b' and turn == 'w') or (board[i - streak_len - 1][j] == 'w' and turn == 'b'):
                opponent_count += 1
        else:  # if streak starts on board margin
            opponent_count += 1

    if direction == "S-W":
        if i + streak_len + 1 < N and j - streak_len - 1 >= 0:
            if (board[i + streak_len + 1][j - streak_len - 1] == 'b' and turn == 'w') or (board[i + streak_len + 1][j - streak_len - 1] == 'w' and turn == 'b'):
                opponent_count += 1
        else:
            opponent_count += 1

    if direction == "S-E":
        if i + streak_len + 1 < N and j + streak_len + 1 < M:
            if (board[i + streak_len + 1][j + streak_len + 1] == 'b' and turn == 'w') or (board[i + streak_len + 1][j + streak_len + 1] == 'w' and turn == 'b'):
                opponent_count += 1
        else:
            opponent_count += 1

    if opponent_count == 0:
        return "open"
    elif opponent_count == 1:
        return "semi-open"
    return "closed"

def GetStrongerHeur1(board, N, M, win_streak):
    if CheckGameOver(board, 'b', win_streak, N, M):
        return -math.inf
    elif CheckGameOver(board, 'w', win_streak, N, M):
        return math.inf
    heur = 0

    for i in range(N):
        ai_horizontal_streak = 0
        human_horizontal_streak = 0
        ai_vertical_streak = 0
        human_vertical_streak = 0
        for j in range(M):
            # current horizontal streak is continued with one checker
            if board[i][j] == 'w':
                ai_horizontal_streak += 1
            # current horizontal streak is discontinued
            else:
                # reward streak with length - 1
                if ai_horizontal_streak > 1:
                    streak_state = GetStreakState(board, N, M, (i, j), ai_horizontal_streak, "left", 'w')
                    if streak_state == "open":
                        heur += pow(ai_horizontal_streak, 2)
                    elif streak_state == "semi-open":
                        heur += pow(ai_horizontal_streak / 2, 2)
                # reset streak
                ai_horizontal_streak = 0

            # current vertical streak is continued with one checker
            if board[j][i] == 'w':
                ai_vertical_streak += 1
            # current vertical streak is discontinued
            else:
                # reward streak with length - 1
                if ai_vertical_streak > 1:
                    streak_state = GetStreakState(board, N, M, (j, i), ai_vertical_streak, "up", 'w')
                    if streak_state == "open":
                        heur += pow(ai_vertical_streak, 2)
                    elif streak_state == "semi-open":
                        heur += pow(ai_vertical_streak / 2, 2)
                # reset streak
                ai_vertical_streak = 0

            # current human horizontal streak is continued with one checker
            if board[i][j] == 'b':
                human_horizontal_streak += 1
            # current human horizontal streak is discontinued
            else:
                # reward streak with -(length - 1)
                if human_horizontal_streak > 1:
                    streak_state = GetStreakState(board, N, M, (i, j), human_horizontal_streak, "left", 'b')
                    if streak_state == "open":
                        heur -= pow(human_horizontal_streak, 2)
                    elif streak_state == "semi-open":
                        heur -= pow(human_horizontal_streak / 2, 2)
                # reset streak
                human_horizontal_streak = 0

            # current human vertical streak is continued with one checker
            if board[j][i] == 'b':
                human_vertical_streak += 1
            # current human vertical streak is discontinued
            else:
                # reward streak with -(length - 1)
                if human_vertical_streak > 1:
                    streak_state = GetStreakState(board, N, M, (j, i), human_vertical_streak, "up", 'b')
                    if streak_state == "open":
                        heur -= pow(human_vertical_streak, 2)
                    elif streak_state == "semi-open":
                        heur -= pow(human_vertical_streak / 2, 2)
                # reset streak
                human_vertical_streak = 0
        if ai_horizontal_streak > 1:
            streak_state = GetStreakState(board, N, M, (i, M), ai_horizontal_streak, "left", 'w')
            if streak_state == "open":
                heur += pow(ai_horizontal_streak, 2)
            elif streak_state == "semi-open":
                heur += pow(ai_horizontal_streak / 2, 2)
        if ai_vertical_streak > 1:
            streak_state = GetStreakState(board, N, M, (N, i), ai_vertical_streak, "up", 'w')
            if streak_state == "open":
                heur += pow(ai_vertical_streak, 2)
            elif streak_state == "semi-open":
                heur += pow(ai_vertical_streak / 2, 2)
        if human_horizontal_streak > 1:
            streak_state = GetStreakState(board, N, M, (i, M), human_horizontal_streak, "left", 'b')
            if streak_state == "open":
                heur -= pow(human_horizontal_streak, 2)
            elif streak_state == "semi-open":
                heur -= pow(human_horizontal_streak / 2, 2)
        if human_vertical_streak > 1:
            streak_state = GetStreakState(board, N, M, (N, i), human_vertical_streak, "up", 'b')
            if streak_state == "open":
                heur -= pow(human_vertical_streak, 2)
            elif streak_state == "semi-open":
                heur -= pow(human_vertical_streak / 2, 2)
    
    for i in range(N):
        ai_diag2_streak = 0
        human_diag2_streak = 0
        ai_diag_streak = 0
        human_diag_streak = 0
        l = i
        c = 0
        while l >= 0 and c < M:
            if board[l][c] == 'w':
                ai_diag2_streak += 1
            else:
                if ai_diag2_streak > 1:
                    streak_state = GetStreakState(board, N, M, (l, c), ai_diag2_streak, "S-W", 'w')
                    if streak_state == "open":
                        heur += pow(ai_diag2_streak, 2)
                    elif streak_state == "semi-open":
                        heur += pow(ai_diag2_streak / 2, 2)
                    # reset streak
                ai_diag2_streak = 0

            if board[l][c] == 'b':
                human_diag2_streak += 1
            else:
                if human_diag2_streak > 1:
                    streak_state = GetStreakState(board, N, M, (l, c), human_diag2_streak, "S-W", 'b')
                    if streak_state == "open":
                        heur -= pow(human_diag2_streak, 2)
                    elif streak_state == "semi-open":
                        heur -= pow(human_diag2_streak / 2, 2)
                    # reset streak
                human_diag2_streak = 0

            if board[l][M - c - 1] == 'w':
                ai_diag_streak += 1
            else:
                if ai_diag_streak > 1:
                    streak_state = GetStreakState(board, N, M, (l, c), ai_diag_streak, "S-E", 'w')
                    if streak_state == "open":
                        heur += pow(ai_diag_streak, 2)
                    elif streak_state == "semi-open":
                        heur += pow(ai_diag_streak / 2, 2)
                    # reset streak
                ai_diag_streak = 0

            if board[l][M - c - 1] == 'b':
                human_diag_streak += 1
            else:
                if human_diag_streak > 1:
                    streak_state = GetStreakState(board, N, M, (l, c), human_diag_streak, "S-E", 'b')
                    if streak_state == "open":
                        heur -= pow(human_diag_streak, 2)
                    elif streak_state == "semi-open":
                        heur -= pow(human_diag_streak/2, 2)
                    # reset streak
                human_diag_streak = 0
            c += 1
            l -= 1

        if ai_diag2_streak > 1:
            streak_state = GetStreakState(board, N, M, (l, c), ai_diag2_streak, "S-W", 'w')
            if streak_state == "open":
                heur += pow(ai_diag2_streak, 2)
            elif streak_state == "semi-open":
                heur += pow(ai_diag2_streak / 2, 2)
        if human_diag2_streak > 1:
            streak_state = GetStreakState(board, N, M, (l, c), human_diag2_streak, "S-W", 'b')
            if streak_state == "open":
                heur -= pow(human_diag2_streak, 2)
            elif streak_state == "semi-open":
                heur -= pow(human_diag2_streak / 2, 2)
        if ai_diag_streak > 1:
            streak_state = GetStreakState(board, N, M, (l, M - c - 1), ai_diag_streak, "S-E", 'w')
            if streak_state == "open":
                heur += pow(ai_diag_streak, 2)
            elif streak_state == "semi-open":
                heur += pow(ai_diag_streak / 2, 2)
        if human_diag_streak > 1:
            streak_state = GetStreakState(board, N, M, (l,M - c - 1), human_diag_streak, "S-E", 'b')
            if streak_state == "open":
                heur -= pow(human_diag_streak, 2)
            elif streak_state == "semi-open":
                heur -= pow(human_diag_streak / 2, 2)
    return heur


def MakeMove(board, turn, move):
    if board[move[0]][move[1]] != " ":
        return False
    board[move[0]][move[1]] = turn

    return True

def UndoMove(board, move):
    board[move[0]][move[1]] = " "

def GetMinimaxMove1(board, N, M, depth, turn, win_streak=5, alpha=-math.inf, beta=math.inf):
    if turn == 'w':
        best_choice = [-math.inf, [-1, -1]]
    else:
        best_choice = [math.inf, [-1, -1]]
    oppoTurn = 'b' if turn == 'w' else 'w'
    if depth <= 0 or CheckGameOver(board, oppoTurn,win_streak, N, M):
        return [GetStrongerHeur1(board, N, M, win_streak), [-1, -1]]

    all_moves = GetAllCandidateMoves(board, N, M, 2)
    for move in all_moves:
        
        MakeMove(board, turn, move)
        child_node_value = GetMinimaxMove1(board, N, M, depth - 1, oppoTurn, win_streak, alpha, beta)
        child_node_value[1] = move

        UndoMove(board, move)
        if turn == 'w' and child_node_value[0] > best_choice[0]:
            best_choice = child_node_value
            alpha = best_choice[0]

        if turn == 'b' and child_node_value[0] < best_choice[0]:
            best_choice = child_node_value
            beta = best_choice[0]
        if alpha >= beta:
            break

    return best_choice

def GetStrongerHeur2(board, N, M, win_streak):
    if CheckGameOver(board, 1, win_streak, N, M):
        return -math.inf
    elif CheckGameOver(board, -1, win_streak, N, M):
        return math.inf

    heur = 0
    for i in range(N):
        ai_horizontal_streak = 0
        human_horizontal_streak = 0
        ai_vertical_streak = 0
        human_vertical_streak = 0
        for j in range(M):
            # current horizontal streak is continued with one checker
            if board[i][j] == 'w':
                ai_horizontal_streak += 1
            # current horizontal streak is discontinued
            else:
                # reward streak with length - 1
                if ai_horizontal_streak > 1:
                    streak_state = GetStreakState(board, N, M, (i, j), ai_horizontal_streak, "left", 'w')
                    if streak_state == "open":
                        heur += pow(10, ai_horizontal_streak)
                    elif streak_state == "semi-open":
                        heur += pow(10, ai_horizontal_streak - 1)
                    # heur += ai_horizontal_streak - 1
                # reset streak
                ai_horizontal_streak = 0

            # current vertical streak is continued with one checker
            if board[j][i] == 'w':
                ai_vertical_streak += 1
            # current vertical streak is discontinued
            else:
                # reward streak with length - 1
                if ai_vertical_streak > 1:
                    streak_state = GetStreakState(board, N, M, (j, i), ai_vertical_streak, "up", 'w')
                    if streak_state == "open":
                        heur += pow(10, ai_vertical_streak)
                    elif streak_state == "semi-open":
                        heur += pow(10, ai_vertical_streak - 1)
                # reset streak
                ai_vertical_streak = 0

            # current human horizontal streak is continued with one checker
            if board[i][j] == 'b':
                human_horizontal_streak += 1
            # current human horizontal streak is discontinued
            else:
                # reward streak with -(length - 1)
                if human_horizontal_streak > 1:
                    streak_state = GetStreakState(board, N, M, (i, j), human_horizontal_streak, "left", 'b')
                    if streak_state == "open":
                        heur -= pow(10, human_horizontal_streak)
                    elif streak_state == "semi-open":
                        heur -= pow(10, human_horizontal_streak - 1)
                # reset streak
                human_horizontal_streak = 0

            # current human vertical streak is continued with one checker
            if board[j][i] == 'b':
                human_vertical_streak += 1
            # current human vertical streak is discontinued
            else:
                # reward streak with -(length - 1)
                if human_vertical_streak > 1:
                    streak_state = GetStreakState(board, N, M, (j, i), human_vertical_streak, "up", 'b')
                    if streak_state == "open":
                        heur -= pow(10, human_vertical_streak)
                    elif streak_state == "semi-open":
                        heur -= pow(10, human_vertical_streak - 1)
                # reset streak
                human_vertical_streak = 0
        if ai_horizontal_streak > 1:
            streak_state = GetStreakState(board, N, M, (i, M), ai_horizontal_streak, "left", 'w')
            if streak_state == "open":
                heur += pow(10, ai_horizontal_streak)
            elif streak_state == "semi-open":
                heur += pow(10, ai_horizontal_streak - 1)
        if ai_vertical_streak > 1:
            streak_state = GetStreakState(board, N, M, (N, i), ai_vertical_streak, "up", 'w')
            if streak_state == "open":
                heur += pow(10, ai_vertical_streak)
            elif streak_state == "semi-open":
                heur += pow(10, ai_vertical_streak - 1)
        if human_horizontal_streak > 1:
            streak_state = GetStreakState(board, N, M, (i, M), human_horizontal_streak, "left", 'b')
            if streak_state == "open":
                heur -= pow(10, human_horizontal_streak)
            elif streak_state == "semi-open":
                heur -= pow(10, human_horizontal_streak - 1)
        if human_vertical_streak > 1:
            streak_state = GetStreakState(board, N, M, (N, i), human_vertical_streak, "up", 'b')
            if streak_state == "open":
                heur -= pow(10, human_vertical_streak)
            elif streak_state == "semi-open":
                heur -= pow(10, human_vertical_streak - 1)


    for i in range(N):
        ai_diag2_streak = 0
        human_diag2_streak = 0
        ai_diag_streak = 0
        human_diag_streak = 0
        l = i
        c = 0
        while l >= 0 and c < M:
            if board[l][c] == 'w':
                ai_diag2_streak += 1
            else:
                if ai_diag2_streak > 1:
                    streak_state = GetStreakState(board, N, M, (l, c), ai_diag2_streak, "S-W", 'w')
                    if streak_state == "open":
                        heur += pow(10, ai_diag2_streak)
                    elif streak_state == "semi-open":
                        heur += pow(10, ai_diag2_streak - 1)
                    # reset streak
                ai_diag2_streak = 0

            if board[l][c] == 'b':
                human_diag2_streak += 1
            else:
                if human_diag2_streak > 1:
                    streak_state = GetStreakState(board, N, M, (l, c), human_diag2_streak, "S-W", 'b')
                    if streak_state == "open":
                        heur -= pow(10, human_diag2_streak)
                    elif streak_state == "semi-open":
                        heur -= pow(10, human_diag2_streak - 1)
                    # reset streak
                human_diag2_streak = 0

            if board[l][M - c - 1] == 'w':
                ai_diag_streak += 1
            else:
                if ai_diag_streak > 1:
                    streak_state = GetStreakState(board, N, M, (l, c), ai_diag_streak, "S-E", 'w')
                    if streak_state == "open":
                        heur += pow(10, ai_diag_streak)
                    elif streak_state == "semi-open":
                        heur += pow(10, ai_diag_streak - 1)
                    # reset streak
                ai_diag_streak = 0

            if board[l][M - c - 1] == 'b':
                human_diag_streak += 1
            else:
                if human_diag_streak > 1:
                    streak_state = GetStreakState(board, N, M, (l, c), human_diag_streak, "S-E", 'b')
                    if streak_state == "open":
                        heur -= pow(10, human_diag_streak)
                    elif streak_state == "semi-open":
                        heur -= pow(10, human_diag_streak - 1)
                    # reset streak
                human_diag_streak = 0
            c += 1
            l -= 1

        if ai_diag2_streak > 1:
            streak_state = GetStreakState(board, N, M, (l, c), ai_diag2_streak, "S-W", 'w')
            if streak_state == "open":
                heur += pow(10, ai_diag2_streak)
            elif streak_state == "semi-open":
                heur += pow(10, ai_diag2_streak - 1)
        if human_diag2_streak > 1:
            streak_state = GetStreakState(board, N, M, (l, c), human_diag2_streak, "S-W", 'b')
            if streak_state == "open":
                heur -= pow(10, human_diag2_streak)
            elif streak_state == "semi-open":
                heur -= pow(10, human_diag2_streak - 1)
        if ai_diag_streak > 1:
            streak_state = GetStreakState(board, N, M, (l, M - c - 1), ai_diag_streak, "S-E", 'w')
            if streak_state == "open":
                heur += pow(10, ai_diag_streak)
            elif streak_state == "semi-open":
                heur += pow(10, ai_diag_streak - 1)
        if human_diag_streak > 1:
            streak_state = GetStreakState(board, N, M, (l,M - c - 1), human_diag_streak, "S-E", 'b')
            if streak_state == "open":
                heur -= pow(10, human_diag_streak)
            elif streak_state == "semi-open":
                heur -= pow(10, human_diag_streak - 1)

    return heur


def GetMinimaxMove2(board, N, M, depth, turn, win_streak=5, alpha=-math.inf, beta=math.inf):
    if turn == 'w':
        best_choice = [-math.inf, [-1, -1]]
    else:
        best_choice = [math.inf, [-1, -1]]
    oppoTurn = 'b' if turn == 'w' else 'w'
    if depth <= 0 or CheckGameOver(board, oppoTurn,win_streak, N, M):
        return [GetStrongerHeur2(board, N, M, win_streak), [-1, -1]]

    all_moves = GetAllCandidateMoves(board, N, M, 2)
    for move in all_moves:
        
        MakeMove(board, turn, move)
        child_node_value = GetMinimaxMove2(board, N, M, depth - 1, oppoTurn, win_streak, alpha, beta)
        child_node_value[1] = move

        UndoMove(board, move)
        if turn == 'w' and child_node_value[0] > best_choice[0]:
            best_choice = child_node_value
            alpha = best_choice[0]

        if turn == 'b' and child_node_value[0] < best_choice[0]:
            best_choice = child_node_value
            beta = best_choice[0]
        if alpha >= beta:
            break

    return best_choice

def DoComputerMove2():
    global board, size
    comp_move = GetMinimaxMove2(board, N=size, M=size, depth=2, turn='w')
    # board[comp_move[1][0]][comp_move[1][1]] = 'w'
    return (comp_move[1][0],comp_move[1][1])

def ClickLevel2(x = 0,y = 0):
    global board,colors,win, move_history, num_click
    num_click += 1
    
    # x,y = getindexposition(x,y)
    # randommove or weak_heursitic
    x, y = UseWeakHeuristic(8, 8)
    # print(x, y)
    
    if x == -1 and y == -1 and len(move_history) != 0:
        x, y = move_history[-1]
     
        del(move_history[-1])
        board[x][y] = " "
        x, y = move_history[-1]
       
        del(move_history[-1])
        board[x][y] = " "
        return
    
    if not CheckIsIn(board, y, x):
        return
    
    if board[x][y] == ' ':
        
        DrawStone(x,y,colors['b'])
        board[x][y]='b'
        
        move_history.append((x, y))
        
        game_res = CheckIsWin(board)
        if game_res in ["White won", "Black won", "Draw"]:
            # print (game_res)
            win = True
            messagebox.showinfo("Result", game_res + f" in {num_click} moves")
            ResetBoard()
            
        ax,ay = DoComputerMove2()
        DrawStone(ax,ay,colors['w'])
        board[ax][ay]='w'    
            
        move_history.append((ax, ay))
        
        game_res = CheckIsWin(board)
        if game_res in ["White won", "Black won", "Draw"]:
            # print (game_res)
            win = True
            messagebox.showinfo("Result", game_res + f" in {num_click} moves")
            ResetBoard()
    # print(board)

def PlayLevel2():
    global screen, board, size, num_click, label_level
    label_level.configure(text="VS: Level 2") 
    num_click = 0
    board = MakeEmptyBoard(size)
    screen.onclick(ClickLevel2)

def ClickLevel1(x = 0,y = 0):
    global board,colors,win, move_history, num_click
    num_click += 1
    
    # x,y = getindexposition(x,y)
    # randommove or weak_heursitic
    x, y = UseWeakHeuristic(8, 8)
    print(x, y)
    
    if x == -1 and y == -1 and len(move_history) != 0:
        x, y = move_history[-1]
     
        del(move_history[-1])
        board[x][y] = " "
        x, y = move_history[-1]
       
        del(move_history[-1])
        board[x][y] = " "
        return
    
    if not CheckIsIn(board, y, x):
        return
    
    if board[x][y] == ' ':
        
        DrawStone(x,y,colors['b'])
        board[x][y]='b'
        
        move_history.append((x, y))
        
        game_res = CheckIsWin(board)
        if game_res in ["White won", "Black won", "Draw"]:
            # print (game_res)
            win = True
            messagebox.showinfo("Result", game_res + f" in {num_click} moves")
            ResetBoard()
            
        ax,ay = DoComputerMove1()
        DrawStone(ax,ay,colors['w'])
        board[ax][ay]='w'    
            
        move_history.append((ax, ay))
        
        game_res = CheckIsWin(board)
        if game_res in ["White won", "Black won", "Draw"]:
            # print (game_res)
            win = True
            messagebox.showinfo("Result", game_res + f" in {num_click} moves")
            ResetBoard()
    # print(board)

def PlayLevel1():
    global screen, board, size, num_click, label_level
    label_level.configure(text="VS: Level 1")
    num_click = 0
    board = MakeEmptyBoard(size)
    screen.onclick(ClickLevel1)

def Initialize(sizeBoard):
    global win,board,screen,colors, move_history,size, num_click, label_level

    turtle.title('AI Assginment 2 - Gomoku')

    size = sizeBoard
    
    move_history = []
    win = False
    board = MakeEmptyBoard(size)
    
    screen = turtle.Screen()
    screen.cv._rootwindow.resizable(False, False)

    screen.setup(screen.screensize()[1]*2.3,screen.screensize()[1]*2.1)
    screen.setworldcoordinates(-1,size,size+3.5,-1)
    screen.bgcolor('orange')
    screen.tracer(500)

    colors = {'w':turtle.Turtle(),'b':turtle.Turtle(), 'g':turtle.Turtle()}
    colors['w'].color('white')
    colors['b'].color('black')

    for key in colors:
        colors[key].ht()
        colors[key].penup()
        colors[key].speed(0)


    border = turtle.Turtle()
    border.speed(9)
    border.penup()

    side = (size-1)/2
    i=-1
    for start in range(size):
        border.goto(start,side + side *i)    
        border.pendown()
        i*=-1
        border.goto(start,side + side *i)     
        border.penup()
        
    i=1
    for start in range(size):
        border.goto(side + side *i,start)
        border.pendown()
        i *= -1
        border.goto(side + side *i,start)
        border.penup()
        
    border.ht()

    canvas = screen.getcanvas() 

    customtkinter.set_appearance_mode("system")  # Modes: system (default), light, dark
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green
    frame = customtkinter.CTkFrame(master=canvas.master,
                                width=140,
                               height=380,
                               bd=7,
                               fg_color="grey",
                               bg_color="grey",
                               relief = "ridge",)
    frame.place(relx=0.88, rely=0.47, anchor="center")

    label = customtkinter.CTkLabel(frame,
                                text="DIFFICULTY",
                                width=110,
                                height=25,
                                fg_color=("skyblue", "gray75"),
                                text_font=("Roboto", 14),
                                corner_radius=10)
    label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

    label_level = customtkinter.CTkLabel(frame,
                                text="Choose a level",
                                width=110,
                                height=25,
                                fg_color=("pink", "gray75"),
                                text_font=("Roboto", 10),
                                corner_radius=10)
    label_level.place(relx=0.5, rely=0.22, anchor=tk.CENTER)

    buttonEasy = customtkinter.CTkButton(frame, text="Level 1", command = lambda: PlayLevel1(), fg_color = "lightgreen", bg_color = "grey")
    buttonEasy.place(relx=0.5, rely=0.34, anchor=tk.CENTER)

    buttonMedium = customtkinter.CTkButton(frame, text="Level 2", command = lambda: PlayLevel2(),fg_color = "yellow", bg_color = "grey")
    buttonMedium.place(relx=0.5, rely=0.46, anchor=tk.CENTER)
    
    buttonHard = customtkinter.CTkButton(frame, text="Level 3", command = lambda: PlayLevel3(), fg_color = "red", bg_color = "grey")
    buttonHard.place(relx=0.5, rely=0.58, anchor=tk.CENTER)

    label_agent = customtkinter.CTkLabel(frame,
                                text="AGENTS",
                                width=110,
                                height=25,
                                fg_color=("skyblue", "gray75"),
                                text_font=("Roboto", 14),
                                corner_radius=10)
    label_agent.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    white_agent = customtkinter.CTkLabel(frame,
                                text="Search Agent",
                                width=110,
                                height=25,
                                fg_color="white",
                                text_font=("Roboto", 10),
                                corner_radius=10)
    white_agent.place(relx=0.5, rely=0.81, anchor=tk.CENTER)

    black_agent = customtkinter.CTkLabel(frame,
                                text="Random Agent",
                                width=110,
                                height=25,
                                text_color="white",
                                fg_color="black",
                                text_font=("Roboto", 10),
                                corner_radius=10)
    black_agent.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    turtle.done()

if __name__ == '__main__':
    Initialize(15)