import gym
import gym_chess
import chess
import chess.svg
import imageio
import cairosvg

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

def evaluate(board, player_color):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == player_color else -value
    score += 0.1 * len(list(board.legal_moves)) if board.turn == player_color else -0.1 * len(list(board.legal_moves))

    # Add penalty for repetition
    if len(board.move_stack) >= 2:
        last_move = board.move_stack[-1]
        second_last_move = board.move_stack[-2]
        
        if last_move.to_square == second_last_move.from_square and last_move.from_square == second_last_move.to_square:
            # Piece moved and moved back: repetition detected
            score -= 50  # or whatever penalty you want

    return score


def minimax(board, depth, maximizing_player, player_color):
    if depth == 0 or board.is_game_over():
        return evaluate(board, player_color)
    best = float('-inf') if maximizing_player else float('inf')
    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, not maximizing_player, player_color)
        board.pop()
        best = max(best, eval) if maximizing_player else min(best, eval)
    return best


def best_move(board, depth):
    player_color = board.turn  # Save who is moving now
    best_eval = float('-inf')
    best_mv = None
    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, False, player_color)
        board.pop()
        if eval > best_eval:
            best_eval = eval
            best_mv = move
    return best_mv


def render_board_to_png(board):
    svg_data = chess.svg.board(board=board, size=512)
    return cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))

def play_game(video_name="chess_minimax.mp4"):
    env = gym.make("Chess-v0")
    obs = env.reset()
    board = env._board
    done = False

    writer = imageio.get_writer(video_name, fps=1)  # 1 frame per second

    while not done:
        png_bytes = render_board_to_png(board.copy())
        writer.append_data(imageio.v2.imread(png_bytes, format='png'))

        if board.turn == chess.BLACK:
            move = best_move(board, 3)
            print(move)
        else:
            move = best_move(board, 2)
            print(move)

        if move is None:
            break

        obs, reward, done, info = env.step(move)

        if board.is_game_over():
            png_bytes = render_board_to_png(board.copy())
            writer.append_data(imageio.v2.imread(png_bytes, format='png'))
            print(env._board.result())
            break

    writer.close()
    env.close()
    print(f"Video saved as {video_name}")

if __name__ == "__main__":
    play_game()
