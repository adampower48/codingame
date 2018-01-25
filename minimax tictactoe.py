from numpy import random


def evaluate(board):
    # Rows
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            if board[i][0] == player:
                return 10
            elif board[i][0] == opponent:
                return -10

    # Columns
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i]:
            if board[0][i] == player:
                return 10
            elif board[0][i] == opponent:
                return -10

    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] or board[0][2] == board[1][1] == board[2][0]:
        if board[1][1] == player:
            return 10
        elif board[1][1] == opponent:
            return -10

    return 0


def minimax(board, depth, is_max, alpha=-1000, beta=1000, hash_value=0):
    global calls
    calls += 1
    score = evaluate(board)

    if score == -10 or score == 10:
        return score

    if not is_moves_left(board):
        return 0

    # print("a:", alpha, "B:", beta)
    if is_max:
        best = -1000

        for i in range(len(board)):
            for k in range(len(board[i])):
                cell = board[i][k]
                if cell == empty:
                    piece = piece_index(player)
                    board[i][k] = player
                    hash_value ^= hash_table[i][k][piece]
                    if hash_value in evaluated_hashes:
                        value = evaluated_hashes[hash_value]
                    else:
                        value = minimax(board, depth + 1, not is_max, alpha, beta, hash_value)
                        evaluated_hashes[hash_value] = value

                    board[i][k] = empty
                    best = max(best, value)
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        i = len(board)
                        break

        return best

    else:
        best = 1000

        for i in range(len(board)):
            for k in range(len(board[i])):
                cell = board[i][k]
                if cell == empty:
                    piece = piece_index(opponent)
                    board[i][k] = opponent
                    hash_value ^= hash_table[i][k][piece]
                    if hash_value in evaluated_hashes:
                        value = evaluated_hashes[hash_value]
                    else:
                        value = minimax(board, depth + 1, not is_max, alpha, beta, hash_value)
                        evaluated_hashes[hash_value] = value
                    board[i][k] = empty
                    best = min(best, value)
                    beta = min(beta, best)
                    if beta <= alpha:
                        i = len(board)
                        break

        return best


def find_best_move(board):
    best_move = (-1, -1)
    best_val = -1000
    hash_value = compute_hash(board)

    for i, row in enumerate(board):
        for k, cell in enumerate(row):
            if cell == empty:
                piece = piece_index(player)
                board[i][k] = player
                hash_value ^= hash_table[i][k][piece]
                if hash_value in evaluated_hashes:
                    move_val = evaluated_hashes[hash_value]
                else:
                    move_val = minimax(board, 0, False, hash_value=hash_value)
                    evaluated_hashes[hash_value] = move_val

                board[i][k] = empty
                hash_value ^= hash_table[i][k][piece]

                print("Testing:", i, k, move_val)

                if move_val > best_val:
                    best_val = move_val
                    best_move = (i, k)

    return best_move


def is_moves_left(board):
    for row in board:
        if "_" in row:
            return True
    return False


def piece_index(piece):
    try:
        return piece_set.index(piece)
    except ValueError:
        return -1


def init_hash_table():
    random.seed(has_seed)
    return random.randint(0, 2 ** 63 - 1, (3, 3, 2), "int64").tolist()


def compute_hash(board):
    h = 0
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell != empty:
                piece_ind = piece_index(cell)
                h ^= hash_table[i][j][piece_ind]
    return h


board = [["_", "_", "_"],
         ["_", "_", "_"],
         ["_", "_", "_"]]
evaluated_hashes = {}

player = "x"
opponent = "o"
empty = "_"
piece_set = "xo"
calls = 0
has_seed = 1234567890
hash_table = init_hash_table()
print(find_best_move(board))
print("Calls:", calls)
