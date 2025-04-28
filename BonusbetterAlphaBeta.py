import gym
import gym_chess
import chess
import chess.svg
import imageio
import cairosvg
import time

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

TT = {}  # Transposition table

def evaluate(board, player_color):
    if board.is_checkmate():
        if board.turn == player_color:
            return -99999
        else:
            return 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == player_color else -value

    # Bonus for mobility
    score += 0.1 * len(list(board.legal_moves)) if board.turn == player_color else -0.1 * len(list(board.legal_moves))

    # Penalty for repetition
    if len(board.move_stack) >= 2:
        last_move = board.move_stack[-1]
        second_last_move = board.move_stack[-2]
        if last_move.to_square == second_last_move.from_square and last_move.from_square == second_last_move.to_square:
            score -= 50

    return score

def order_moves(board):
    """Prioritize captures first"""
    moves = list(board.legal_moves)
    moves.sort(key=lambda move: board.is_capture(move), reverse=True)
    return moves

def quiescence(board, alpha, beta, player_color):
    stand_pat = evaluate(board, player_color)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiescence(board, -beta, -alpha, player_color)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha

def alphabeta(board, depth, alpha, beta, maximizing_player, player_color):
    board_key = board.fen()
    if board_key in TT:
        return TT[board_key]

    if depth == 0:
        return quiescence(board, alpha, beta, player_color)

    if maximizing_player:
        max_eval = float('-inf')
        for move in order_moves(board):
            board.push(move)
            eval = alphabeta(board, depth-1, alpha, beta, False, player_color)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        TT[board_key] = max_eval
        return max_eval
    else:
        min_eval = float('inf')
        for move in order_moves(board):
            board.push(move)
            eval = alphabeta(board, depth-1, alpha, beta, True, player_color)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        TT[board_key] = min_eval
        return min_eval

def best_move(board, max_depth, time_limit=5.0):
    start_time = time.time()
    player_color = board.turn
    best_mv = None

    for depth in range(1, max_depth + 1):
        alpha = float('-inf')
        beta = float('inf')
        local_best = None
        best_eval = float('-inf')

        for move in order_moves(board):
            if time.time() - start_time > time_limit:
                print(f"Time limit hit at depth {depth}")
                return best_mv

            board.push(move)
            eval = alphabeta(board, depth-1, alpha, beta, False, player_color)
            board.pop()

            if eval > best_eval:
                best_eval = eval
                local_best = move
            alpha = max(alpha, best_eval)

        if time.time() - start_time > time_limit:
            break

        best_mv = local_best
        print(f"Depth {depth} best move: {best_mv} eval: {best_eval}")

    return best_mv

def render_board_to_png(board):
    svg_data = chess.svg.board(board=board, size=350)
    return cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))

def play_game(video_name="chess_game_fast.mp4"):
    env = gym.make("Chess-v0")
    obs = env.reset()
    board = env._board
    done = False

    writer = imageio.get_writer(video_name, fps=1)

    while not done:
        png_bytes = render_board_to_png(board.copy())
        writer.append_data(imageio.v2.imread(png_bytes, format='png'))

        move = best_move(board, max_depth=12, time_limit=5.0)
        print(f"Move: {move}")

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
