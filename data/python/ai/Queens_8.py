def is_safe(board, row, col):
    """Check if a queen can be placed at board[row][col]."""
    # Check column
    for i in range(row):
        if board[i][col] == 1:
            return False

    # Check upper-left diagonal
    i, j = row, col
    while i >= 0 and j >= 0:
        if board[i][j] == 1:
            return False
        i -= 1
        j -= 1

    # Check upper-right diagonal
    i, j = row, col
    while i >= 0 and j < len(board):
        if board[i][j] == 1:
            return False
        i -= 1
        j += 1

    return True


def solve_queen(board, row):
    """Try to place queens row by row."""
    n = len(board)
    if row >= n:  # All queens placed
        return True

    for col in range(n):
        if is_safe(board, row, col):
            board[row][col] = 1  # Place queen

            if solve_queen(board, row + 1):  # Recurse
                return True

            board[row][col] = 0  # Backtrack

    return False


def print_board(board):
    """Print the chessboard with queens."""
    n = len(board)
    for i in range(n):
        for j in range(n):
            print("Q" if board[i][j] else ".", end=" ")
        print()


def solve_8queens():
    n = 8
    board = [[0] * n for _ in range(n)]

    if solve_queen(board, 0):
        print("Solution Found:\n")
        print_board(board)
    else:
        print("Solution not found")


# Run the solver
solve_8queens()
