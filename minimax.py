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

def evaluate(board):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    score += 0.1 * len(list(board.legal_moves)) if board.turn == chess.WHITE else -0.1 * len(list(board.legal_moves))
    return score

def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate(board)
    best = float('-inf') if maximizing_player else float('inf')
    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, not maximizing_player)
        board.pop()
        best = max(best, eval) if maximizing_player else min(best, eval)
    return best

def best_move(board, depth):
    best_eval = float('-inf')
    best_mv = None
    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, False)
        board.pop()
        if eval > best_eval:
            best_eval = eval
            best_mv = move
    return best_mv

def render_board_to_png(board):
    svg_data = chess.svg.board(board=board, size=350)
    return cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))

def play_game(video_name="chess_game.mp4"):
    env = gym.make("Chess-v0")
    obs = env.reset()
    board = env._board
    done = False

    writer = imageio.get_writer(video_name, fps=1)  # 1 frame per second

    while not done:
        png_bytes = render_board_to_png(board.copy())
        writer.append_data(imageio.v2.imread(png_bytes, format='png'))

        if board.turn == chess.WHITE:
            move = best_move(board, 3)
        else:
            move = list(board.legal_moves)[0]

        if move is None:
            break

        obs, reward, done, info = env.step(move)

        if board.is_game_over():
            png_bytes = render_board_to_png(board.copy())
            writer.append_data(imageio.v2.imread(png_bytes, format='png'))
            break

    writer.close()
    env.close()
    print(f"Video saved as {video_name}")

if __name__ == "__main__":
    play_game()
