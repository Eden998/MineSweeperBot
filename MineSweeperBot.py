import os
import pyautogui
import time
import random
from more_itertools import distinct_permutations
import sys
import copy

os.startfile("Winmine.exe")
time.sleep(1)

# for screenshot:
smiley_x, smiley_y = pyautogui.locateCenterOnScreen('smiley.png')
left = smiley_x - 241  # 1038
top = smiley_y + 26  # 425
width = 481
height = 257
# colors:
hidden = (192, 192, 192)
one = (0, 0, 255)
two = (0, 128, 0)
three = (255, 0, 0)
four = (0, 0, 128)
five = (128, 0, 0)
six = (0, 128, 128)
colors = [hidden, one, two, three, four, five, six]
x_top_mine = left + 9
y_top_mine = top + 8
number_of_guesses = 4
board_size = [30, 16]
def initialize_game_board():
    pyautogui.click(x=smiley_x, y=smiley_y)
    enough = False
    while not enough:
        bombed = False
        for guess in range(number_of_guesses):
            randx, randy = random.randint(0, board_size[0] - 1), random.randint(0, board_size[1] - 1)
            pyautogui.click(x=x_top_mine + randx * 16, y=y_top_mine + randy * 16)
        img = pyautogui.screenshot(region=(left, top, width, height))
        board = create_board()
        board = update_board(board)
        count = 0
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] > 0:
                    count += 1
                if img.getpixel((9 + j * 16, 8 + i * 16)) == (0, 0, 0):
                    bombed = True
        if count > 10 and not bombed:
            enough = True
        else:
            pyautogui.click(x=smiley_x, y=smiley_y)
    return board


def is_bombed():
    img = pyautogui.screenshot(region=(left, top, width, height))
    for i in range(16):
        for j in range(30):
            if img.getpixel((9 + j * 16, 8 + i * 16)) == (0, 0, 0):
                return True
    return False


def create_board():
    return [[0 for i in range(board_size[0])] for j in range(board_size[1])]


def finish_board(board):
    for i in range(board_size[1]):
        for j in range(board_size[0]):
            if board[i][j] == 0:
                return False
    return True


def update_board(board):
    img = pyautogui.screenshot(region=(left, top, width, height))
    for i in range(board_size[1]):
        for j in range(board_size[0]):
            if board[i][j] == 0:
                for k in range(len(colors)):
                    if img.getpixel((9 + j * 16, 8 + i * 16)) == colors[k]:
                        if colors[k] == hidden:
                            board[i][j] = k if img.getpixel((j * 16, 8 + i * 16)) == (255, 255, 255) else k - 2
                        else:
                            board[i][j] = k
    return board


def get_cell_from_permutation(board, cell, neighbor_cell):
    if neighbor_cell == 0:
        return (cell[0] - 1, cell[1] - 1)
    elif neighbor_cell == 1:
        return (cell[0] - 1, cell[1])
    elif neighbor_cell == 2:
        return (cell[0] - 1, cell[1] + 1)
    elif neighbor_cell == 3:
        return (cell[0], cell[1] - 1)
    elif neighbor_cell == 4:
        return (cell[0], cell[1] + 1)
    elif neighbor_cell == 5:
        return (cell[0] + 1, cell[1] - 1)
    elif neighbor_cell == 6:
        return (cell[0] + 1, cell[1])
    elif neighbor_cell == 7:
        return (cell[0] + 1, cell[1] + 1)


def get_cell_sides(board, cell):
    ls = []
    for i in range(cell[0] - 1, cell[0] + 2):
        for j in range(cell[1] - 1, cell[1] + 2):
            if (i, j) != cell:
                if i < 0 or i >= board_size[1] or j < 0 or j >= board_size[0]:
                    ls.append(-2)
                else:
                    ls.append(board[i][j])
    return ls


def is_valid(board):
    for i in range(board_size[1]):
        for j in range(board_size[0]):
            cell_value = board[i][j]
            if cell_value > 0:
                cell_sides = get_cell_sides(board, (i, j))
                bombs = 0
                for cell in cell_sides:
                    if cell == -1:
                        bombs += 1
                if bombs > cell_value:
                    return False
    return True


def permutation_possible(cell_value, blocked_spots, bombs_count):
    perms = (cell_value - bombs_count) * "1" + (8 - cell_value + bombs_count) * "0"
    perms = list(distinct_permutations(perms))
    valid_perms = []
    for p in perms:
        valid = True
        for blocked_cell in blocked_spots:
            if p[blocked_cell] == '1':
                valid = False
        if valid:
            valid_perms.append(p)
    return valid_perms

# 1,2,3,4,5,6,7,8 - number on cell
# 0 - hidden cell
# -1 - bomb cell
# -2 - out of map
def check_cell_probabilities(board, cell, prob_rate):
    cell_value = board[cell[0]][cell[1]]
    if cell_value <= 0:
        return None
    prob_list = [0, 0, 0, 0, 0, 0, 0, 0]
    next_squares_values = get_cell_sides(board, cell)
    blocked_spots = [i for i in range(8) if next_squares_values[i] != 0]
    bombs_count = next_squares_values.count(-1)
    perm = permutation_possible(cell_value, blocked_spots, bombs_count)
    total_perms = 0
    for p in perm:
        if check_perm(copy.deepcopy(board), cell, p):
            total_perms += 1
            for i in range(len(prob_list)):
                prob_list[i] += int(p[i])
    bomb_cells = []
    good_cells = []
    for neighbor_cell in range(len(prob_list)):
        if prob_list[neighbor_cell] >= total_perms * prob_rate:
            bomb_cell_row, bomb_cell_col = get_cell_from_permutation(board, cell, neighbor_cell)
            if 0 <= bomb_cell_row < 16 and 0 <= bomb_cell_col < 30 and board[bomb_cell_row][bomb_cell_col] == 0:
                bomb_cells.append((bomb_cell_row, bomb_cell_col))
        if prob_list[neighbor_cell] <= total_perms * (1 - prob_rate):
            good_cell_row, good_cell_col = get_cell_from_permutation(board, cell, neighbor_cell)
            if 0 <= good_cell_row < 16 and 0 <= good_cell_col < 30 and board[good_cell_row][good_cell_col] == 0:
                good_cells.append((good_cell_row, good_cell_col))
    return bomb_cells, good_cells


def check_perm(board, cell, p):
    curr = 0
    for i in range(cell[0] - 1, cell[0] + 2):
        for j in range(cell[1] - 1, cell[1] + 2):
            if (i, j) != cell:
                if p[curr] == '1':
                    board[i][j] = -1
                curr += 1
    return is_valid(board)


game_board = initialize_game_board()
prob_rate = 1
while not finish_board(game_board):
    print(prob_rate)
    if prob_rate == 1:
        game_board = update_board(game_board)
        while is_bombed():
            game_board = initialize_game_board()
            game_board = update_board(game_board)
    if finish_board(game_board):
        sys.exit()
    bomb_spots = []
    good_spots = []
    for i in range(board_size[1]):
        for j in range(board_size[0]):
            if game_board[i][j] > 0:
                prob = check_cell_probabilities(game_board, (i, j), prob_rate)
                bomb_spots.extend(prob[0])
                good_spots.extend(prob[1])
    bomb_spots = list(set(bomb_spots))
    good_spots = list(set(good_spots))
    if len(bomb_spots) == 0 and len(good_spots) == 0:
        prob_rate -= 0.05
    elif len(good_spots) != 0 and prob_rate < 1:
        good_spots = [good_spots[random.randint(0, len(good_spots) - 1)]]
        prob_rate = 1
    else:
        prob_rate = 1
    for bomb in bomb_spots:
        game_board[bomb[0]][bomb[1]] = -1
        pyautogui.click(x=x_top_mine + bomb[1] * 16 , y=y_top_mine + bomb[0] * 16, button='right')
        bomb_spots.remove(bomb)
    for good in good_spots:
        pyautogui.click(x=x_top_mine + good[1] * 16, y=y_top_mine + good[0] * 16)
        good_spots.remove(good)
