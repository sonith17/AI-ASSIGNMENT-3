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

def evaluate(board,color):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == color else -value
    score += 0.1 * len(list(board.legal_moves)) if board.turn == color else -0.1 * len(list(board.legal_moves))
    return score

def minimax(board, depth, maximizing_player,color=chess.WHITE):
    if depth == 0 or board.is_game_over():
        return evaluate(board,color)
    best = float('-inf') if maximizing_player else float('inf')
    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, not maximizing_player,color)
        board.pop()
        best = max(best, eval) if maximizing_player else min(best, eval)
    return best

def best_move(board, depth,color=chess.WHITE):
    best_eval = float('-inf')
    best_mv = None
    for move in board.legal_moves:
        board.push(move)

        if board.is_checkmate():
            print("Checkmate detected, skipping move.")
            board.pop()
            return move
        
        if board.is_stalemate():
            board.pop()
            print("Stalemate detected, skipping move.")
            continue

        eval = minimax(board, depth - 1, False,color)
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

        if board.turn == chess.WHITE:
            move = best_move(board, 3, color=chess.WHITE)
        else:
            move = best_move(board, 3, color=chess.BLACK)

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
