import math

# Constants for representing the players
X = 'X'
O = 'O'
EMPTY = ' '

# Function to print the Tic Tac Toe board
def print_board(board):
    for row in board:
        print(' | '.join(row))
        print('---------')

# Function to check if a player has won
def check_winner(board, player):
    # Check rows
    for row in board:
        if all(cell == player for cell in row):
            return True
    # Check columns
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    # Check diagonals
    if all(board[i][i] == player for i in range(3)) or \
       all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

# Function to check if the board is full
def is_board_full(board):
    return all(cell != EMPTY for row in board for cell in row)

# Function to evaluate the board
def evaluate(board):
    if check_winner(board, X):
        return 1
    elif check_winner(board, O):
        return -1
    else:
        return 0

# Function to get all possible next moves
def get_possible_moves(board):
    moves = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                moves.append((i, j))
    return moves

# Minimax function with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    if check_winner(board, X):
        return 1
    elif check_winner(board, O):
        return -1
    elif is_board_full(board):
        return 0

    if maximizing_player:
        max_eval = -math.inf
        for move in get_possible_moves(board):
            board[move[0]][move[1]] = X
            eval = minimax(board, depth + 1, alpha, beta, False)
            board[move[0]][move[1]] = EMPTY
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in get_possible_moves(board):
            board[move[0]][move[1]] = O
            eval = minimax(board, depth + 1, alpha, beta, True)
            board[move[0]][move[1]] = EMPTY
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# Function to find the best move for the AI
def find_best_move(board):
    best_eval = -math.inf
    best_move = None
    for move in get_possible_moves(board):
        board[move[0]][move[1]] = X
        eval = minimax(board, 0, -math.inf, math.inf, False)
        board[move[0]][move[1]] = EMPTY
        if eval > best_eval:
            best_eval = eval
            best_move = move
    return best_move

# Function to play the game against the AI
def play_game():
    board = [[EMPTY] * 3 for _ in range(3)]
    current_player = X
    while True:
        print_board(board)
        if current_player == X:
            row, col = find_best_move(board)
            print("AI's move:")
            board[row][col] = X
        else:
            while True:
                row = int(input("Enter row (0-2): "))
                col = int(input("Enter column (0-2): "))
                if board[row][col] == EMPTY:
                    break
                else:
                    print("Cell already occupied. Try again.")
            board[row][col] = O

        if check_winner(board, X):
            print_board(board)
            print("AI wins!")
            break
        elif check_winner(board, O):
            print_board(board)
            print("You win!")
            break
        elif is_board_full(board):
            print_board(board)
            print("It's a draw!")
            break

        current_player = O if current_player == X else X

# Play the game
play_game()
