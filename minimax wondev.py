import sys, cProfile
from numpy import random


def evaluate(board):
    for i, row in enumerate(board):
        for k, cell in enumerate(row):
            if cell == "3x":
                return 10
            if cell == "3o":
                return -10

    return 0


def minimax(board, depth, is_max, alpha=-1000, beta=1000, hash_value=0):
    global calls, hashes_successful
    calls += 1
    score = evaluate(board)

    # print("board depth:", depth, file=sys.stderr)
    # for r in board:
    #     print(*r, file=sys.stderr)

    if score == -10 or score == 10:
        return score

    if depth > search_depth:
        return score

    my_units = []
    enemy_units = []
    for i, row in enumerate(board):
        for k, cell in enumerate(row):
            if cell[1] == player:
                my_units.append([k, i])
            elif cell[1] == opponent:
                enemy_units.append([k, i])

    possible_moves = gen_possible_moves(board, is_max)
    # print(*possible_moves)

    if is_max:
        best = -1000

        for move in possible_moves:
            start = [my_units[0][0], my_units[0][1]]
            move_dir = cardinals_chr[move[2]]
            build_dir = cardinals_chr[move[3]]

            # print("Move:", *move, file=sys.stderr)

            # Remove player from cell
            x = start[0]
            y = start[1]
            board[y][x] = board[y][x][0] + empty
            cell_ind = piece_index(board[y][x])
            hash_value ^= hash_table[y][x][cell_ind]

            # Places player on cell
            move_x = x + move_dir[0]
            move_y = y + move_dir[1]
            board[move_y][move_x] = board[move_y][move_x][0] + player
            move_cell_ind = piece_index(board[move_y][move_x])
            hash_value ^= hash_table[move_y][move_x][move_cell_ind]

            # Builds on a cell
            build_x = move_x + build_dir[0]
            build_y = move_y + build_dir[1]
            board[build_y][build_x] = str(int(board[build_y][build_x][0]) + 1) + board[build_y][build_x][
                1]  # add 1 to cell height
            build_cell_ind = piece_index(board[build_y][build_x])
            hash_value ^= hash_table[build_y][build_x][build_cell_ind]

            if hash_value in evaluated_hashes:
                hashes_successful += 1
                value = evaluated_hashes[hash_value]
            else:
                value = minimax(board, depth + 1, not is_max, alpha, beta, hash_value)
                evaluated_hashes[hash_value] = value

            # Undo moves
            hash_value ^= hash_table[build_y][build_x][build_cell_ind]
            board[build_y][build_x] = str(int(board[build_y][build_x][0]) - 1) + board[build_y][build_x][
                1]  # sub 1 to cell height

            hash_value ^= hash_table[move_y][move_x][move_cell_ind]
            board[move_y][move_x] = board[move_y][move_x][0] + empty

            hash_value ^= hash_table[y][x][cell_ind]
            board[y][x] = board[y][x][0] + player

            best = max(best, value)
            alpha = max(alpha, best)
            if beta <= alpha: break

        return best

    else:
        best = 1000

        for move in possible_moves:
            start = [enemy_units[0][0], enemy_units[0][1]]
            move_dir = cardinals_chr[move[2]]
            build_dir = cardinals_chr[move[3]]

            # print("Move:", *move, file=sys.stderr)

            # Remove player from cell
            x = start[0]
            y = start[1]
            board[y][x] = board[y][x][0] + empty
            cell_ind = piece_index(board[y][x])
            hash_value ^= hash_table[y][x][cell_ind]

            # Places player on cell
            move_x = x + move_dir[0]
            move_y = y + move_dir[1]
            board[move_y][move_x] = board[move_y][move_x][0] + opponent
            move_cell_ind = piece_index(board[move_y][move_x])
            hash_value ^= hash_table[move_y][move_x][move_cell_ind]

            # Builds on a cell
            build_x = move_x + build_dir[0]
            build_y = move_y + build_dir[1]
            board[build_y][build_x] = str(int(board[build_y][build_x][0]) + 1) + board[build_y][build_x][
                1]  # add 1 to cell height
            build_cell_ind = piece_index(board[build_y][build_x])
            hash_value ^= hash_table[build_y][build_x][build_cell_ind]

            if hash_value in evaluated_hashes:
                hashes_successful += 1
                value = evaluated_hashes[hash_value]
            else:
                value = minimax(board, depth + 1, not is_max, alpha, beta, hash_value)
                evaluated_hashes[hash_value] = value

            # Undo moves
            hash_value ^= hash_table[build_y][build_x][build_cell_ind]
            board[build_y][build_x] = str(int(board[build_y][build_x][0]) - 1) + board[build_y][build_x][
                1]  # sub 1 to cell height

            hash_value ^= hash_table[move_y][move_x][move_cell_ind]
            board[move_y][move_x] = board[move_y][move_x][0] + empty

            hash_value ^= hash_table[y][x][cell_ind]
            board[y][x] = board[y][x][0] + opponent

            best = min(best, value)
            alpha = min(alpha, best)
            if beta <= alpha: break

        return best


def find_best_move(board):
    best_move = -1
    best_val = -1000
    hash_value = compute_hash(board)

    possible_moves = gen_possible_moves(board)

    for move in possible_moves:
        start = [my_units[0][0], my_units[0][1]]
        move_dir = cardinals_chr[move[2]]
        build_dir = cardinals_chr[move[3]]

        # Remove player from cell
        x = start[0]
        y = start[1]
        board[y][x] = board[y][x][0] + empty
        cell_ind = piece_index(board[y][x])
        hash_value ^= hash_table[y][x][cell_ind]

        # Places player on cell
        move_x = x + move_dir[0]
        move_y = y + move_dir[1]
        board[move_y][move_x] = board[move_y][move_x][0] + player
        move_cell_ind = piece_index(board[move_y][move_x])
        hash_value ^= hash_table[move_y][move_x][move_cell_ind]

        # Builds on a cell
        build_x = move_x + build_dir[0]
        build_y = move_y + build_dir[1]
        board[build_y][build_x] = str(int(board[build_y][build_x][0]) + 1) + board[build_y][build_x][
            1]  # add 1 to cell height
        build_cell_ind = piece_index(board[build_y][build_x])
        hash_value ^= hash_table[build_y][build_x][build_cell_ind]

        if hash_value in evaluated_hashes:
            move_val = evaluated_hashes[hash_value]
        else:
            move_val = minimax(board, 0, False, hash_value=hash_value)
            evaluated_hashes[hash_value] = move_val

        # Undo moves
        hash_value ^= hash_table[build_y][build_x][build_cell_ind]
        board[build_y][build_x] = str(int(board[build_y][build_x][0]) - 1) + board[build_y][build_x][
            1]  # sub 1 to cell height

        hash_value ^= hash_table[move_y][move_x][move_cell_ind]
        board[move_y][move_x] = board[move_y][move_x][0] + empty

        hash_value ^= hash_table[y][x][cell_ind]
        board[y][x] = board[y][x][0] + player

        print("Testing:", move, move_val, file=sys.stderr)

        if move_val > best_val:
            best_val = move_val
            best_move = move

    return best_move


def piece_index(piece):
    try:
        return tile_set.index(piece[0]) * 3 + piece_set.index(piece[1])
    except ValueError:
        return -1


def init_hash_table():
    random.seed(hash_seed)
    return random.randint(0, 2 ** 63 - 1, (SIZE, SIZE, 18), "int64").tolist()


def compute_hash(board):
    h = 0
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            piece_ind = piece_index(cell)
            h ^= hash_table[i][j][piece_ind]
    return h


def gen_possible_moves(board, me=True):
    moves = []
    my_units = []
    enemy_units = []
    for i, row in enumerate(board):
        for k, cell in enumerate(row):
            if cell[1] == player:
                my_units.append([k, i])
            elif cell[1] == opponent:
                enemy_units.append([k, i])

    if me:
        for unit in my_units:
            for offset in cardinals:
                move_coord = [unit[0] + offset[0], unit[1] + offset[1]]
                if not 0 <= move_coord[0] < SIZE or not 0 <= move_coord[1] < SIZE:
                    continue
                if board[move_coord[1]][move_coord[0]][0] in unavailable or board[move_coord[1]][move_coord[0]][
                    1] in piece_set[:2] or int(board[move_coord[1]][move_coord[0]][0]) > int(
                    board[unit[1]][unit[0]][0]) + 1:
                    continue

                move_chr = cardinals_chr[offset]

                for offset2 in cardinals:
                    build_coord = [move_coord[0] + offset2[0], move_coord[1] + offset2[1]]
                    if not 0 <= build_coord[0] < SIZE or not 0 <= build_coord[1] < SIZE:
                        continue
                    if board[build_coord[1]][build_coord[0]][0] in unavailable or (
                            board[build_coord[1]][build_coord[0]][1] in piece_set[:2] and build_coord != unit):
                        continue

                    moves.append(["MOVE&BUILD", 0, move_chr, cardinals_chr[offset2]])

    else:
        for unit in enemy_units:
            for offset in cardinals:
                newCoord = [unit[0] + offset[0], unit[1] + offset[1]]
                if not 0 <= newCoord[0] < SIZE or not 0 <= newCoord[1] < SIZE:
                    continue
                if board[newCoord[1]][newCoord[0]][0] in unavailable or board[newCoord[1]][newCoord[0]][1] in piece_set[
                                                                                                              :2] or int(
                    board[newCoord[1]][newCoord[0]][0]) > int(board[unit[1]][unit[0]][0]) + 1:
                    continue

                move_chr = cardinals_chr[offset]

                for offset2 in cardinals:
                    newBuild = [newCoord[0] + offset2[0], newCoord[1] + offset2[1]]
                    if not 0 <= newBuild[0] < SIZE or not 0 <= newBuild[1] < SIZE:
                        continue
                    if board[newBuild[1]][newBuild[0]][0] in unavailable or board[newBuild[1]][newBuild[0]][
                        1] in piece_set[:2]:
                        continue

                    moves.append(["MOVE&BUILD", 0, move_chr, cardinals_chr[offset2]])

    return moves


def gen_game_board(grid):
    for u in my_units:
        grid[u[1]][u[0]] += player
    for u in enemy_units:
        grid[u[1]][u[0]] += opponent

    for i, row in enumerate(grid):
        for k, cell in enumerate(row):
            if len(cell) == 1:
                grid[i][k] += empty

    return grid


b = [["0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ["0_", "0_", "0o", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ["0_", "0_", "0x", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ["0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ["0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ["0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ["0_", "0_", "0_", "0_", "0_", "0_", "0_", "0o", "0_", "0_", ],
     ["0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ["0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ["0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", "0_", ],
     ]

evaluated_hashes = {}
cardinals = [(-1, 1), (0, 1), (1, 1),
             (-1, 0), (1, 0),
             (-1, -1), (0, -1), (1, -1)]
cardinals_chr = {
    (-1, 1): "SW",
    (0, 1): "S",
    (1, 1): "SE",
    (-1, 0): "W",
    (1, 0): "E",
    (-1, -1): "NW",
    (0, -1): "N",
    (1, -1): "NE",

    "SW": (-1, 1),
    "S": (0, 1),
    "SE": (1, 1),
    "W": (-1, 0),
    "E": (1, 0),
    "NW": (-1, -1),
    "N": (0, -1),
    "NE": (1, -1)
}
unavailable = ".4"
player = "x"
opponent = "o"
empty = "_"
piece_set = "xo_"
tile_set = ".01234"
calls = 0
hash_seed = 1234567890
search_depth = 1
hashes_successful = 0

## GAME LOOP ##

my_units = []
enemy_units = []

SIZE = int(input())
units_per_player = int(input())

hash_table = init_hash_table()


def game():
    global my_units, enemy_units
    grid = [list(input()) for i in range(SIZE)]
    my_units = [[int(j) for j in input().split()] for i in range(units_per_player)]
    enemy_units = [[int(j) for j in input().split()] for i in range(units_per_player)]

    num_legal_actions = int(input())
    legal_actions = []
    for i in range(num_legal_actions):
        atype, index, dir_1, dir_2 = input().split()
        index = int(index)
        legal_actions.append([atype, index, dir_1, dir_2])

    print(num_legal_actions, file=sys.stderr)
    for a in legal_actions:
        print(*a, file=sys.stderr)

    tboard = gen_game_board(grid)

    print("board:", file=sys.stderr)
    for r in tboard:
        print(*r, file=sys.stderr)

    # possible_moves = gen_possible_moves(board)
    winning_move = find_best_move(tboard)

    # print(*legal_actions[random.randint(len(legal_actions) - 1)] if len(legal_actions) > 0 else "HALP!")
    print(*winning_move if winning_move != -1 else "HALP!")


## Move syntax: ["MOVE&BUILD", unit_index, move_dir, build_dir]

# cProfile.run("game()", sort="tottime")

# print("hashes found:", hashes_successful)

while True:
    game()
