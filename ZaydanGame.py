def initialize_board():
    """Create a new 3x3 board."""
    return [' ' for _ in range(9)]

def display_board(board):
    """Print the current state of the board."""
    print("\n")
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print("\n")

def check_win(board, player):
    """Check if the specified player has won."""
    win_conditions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), # Horizontal
        (0, 3, 6), (1, 4, 7), (2, 5, 8), # Vertical
        (0, 4, 8), (2, 4, 6)             # Diagonal
    ]
    for condition in win_conditions:
        if all(board[i] == player for i in condition):
            return True
    return False

def check_draw(board):
    """Check if the game is a draw (board is full)."""
    return ' ' not in board

def get_player_move(board, player):
    """Prompt the current player for a move and validate it."""
    while True:
        try:
            move = input(f"Player {player}, enter your move (1-9): ")
            move = int(move) - 1 # Convert to 0-8 index
            
            if 0 <= move <= 8 and board[move] == ' ':
                return move
            elif 0 <= move <= 8 and board[move] != ' ':
                print("That spot is already taken. Try again.")
            else:
                print("Invalid input. Please choose a number between 1 and 9.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def play_game():
    """Main game loop."""
    board = initialize_board()
    current_player = 'X'
    game_running = True

    print("Welcome to Tic-Tac-Toe!")
    print("Positions are numbered 1-9 as follows:")
    print(" 1 | 2 | 3 ")
    print("---+---+---")
    print(" 4 | 5 | 6 ")
    print("---+---+---")
    print(" 7 | 8 | 9 \n")

    while game_running:
        display_board(board)
        move = get_player_move(board, current_player)
        board[move] = current_player

        if check_win(board, current_player):
            display_board(board)
            print(f"🎉 Player {current_player} wins! 🎉")
            game_running = False
        elif check_draw(board):
            display_board(board)
            print("🤝 It's a draw! 🤝")
            game_running = False
        else:
            # Switch players
            current_player = 'O' if current_player == 'X' else 'X'

if __name__ == "__main__":
    play_game()
