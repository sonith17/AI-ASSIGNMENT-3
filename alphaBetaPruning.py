import gym
import gym_chess
import chess
import chess.svg
import imageio
import cairosvg

# Piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 9000,
    chess.KING: 0  # King value is special
}

CENTER_SQUARES = {chess.D4, chess.D5, chess.E4, chess.E5}

def evaluate(board, player_color):
    score = 0
    opponent_color = not player_color

    # Material and positional score
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES.get(piece.piece_type, 0)
            multiplier = 1 if piece.color == player_color else -1
            score += multiplier * value

            # Central control bonus
            if square in CENTER_SQUARES:
                score += multiplier * 10

    # Mobility (scaled)
    mobility = len(list(board.legal_moves))
    mobility_factor = 0.2
    score += mobility_factor * mobility if board.turn == player_color else -mobility_factor * mobility

    # Repetition penalty
    if _is_repetition(board):
        score -= 500

    # Basic king safety (bonus if castled)
    player_king = board.king(player_color)
    if player_king and (board.has_kingside_castling_rights(player_color) or board.has_queenside_castling_rights(player_color)):
        score += 30

    opponent_king = board.king(opponent_color)
    if opponent_king and (board.has_kingside_castling_rights(opponent_color) or board.has_queenside_castling_rights(opponent_color)):
        score -= 30

    return score


def _is_repetition(board):
    """Detects if last two full plies reverse each other (back-and-forth)."""
    if len(board.move_stack) < 4:
        return False

    w1, b2, w3, b4 = board.move_stack[-4], board.move_stack[-3], board.move_stack[-2], board.move_stack[-1]
    return (w1.from_square == w3.to_square and
            w1.to_square == w3.from_square and
            b2.from_square == b4.to_square and
            b2.to_square == b4.from_square)

# Order moves: captures first, then others
def order_moves(board):
    moves = []
    for move in board.legal_moves:
        score = 0
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                score += PIECE_VALUES[captured_piece.piece_type]  # capture valuable pieces first
            score += 1000  # prefer captures in general
        if board.gives_check(move):
            score += 500  # prefer checks
        moves.append((score, move))
    
    moves.sort(reverse=True, key=lambda x: x[0])  # highest score first
    return [move for _, move in moves]

# Alpha-beta minimax with move ordering
def alphabeta(board, depth, alpha, beta, maximizing_player, player_color):
    if depth == 0 or board.is_game_over():
        return evaluate(board, player_color)

    if maximizing_player:
        max_eval = float('-inf')
        for move in order_moves(board):
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, False, player_color)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        return max_eval
    else:
        min_eval = float('inf')
        for move in order_moves(board):
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, True, player_color)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval

def best_move(board, depth):
    player_color = board.turn
    best_eval = float('-inf')
    best_mv = None
    alpha = float('-inf')
    beta = float('inf')

    for move in order_moves(board):
        board.push(move)
        
        if board.is_checkmate():
            print("Checkmate detected, skipping move.")
            board.pop()
            return move
        
        if board.is_stalemate():
            board.pop()
            print("Stalemate detected, skipping move.")
            continue

        eval = alphabeta(board, depth - 1, alpha, beta, False, player_color)
        board.pop()
        if eval > best_eval:
            best_eval = eval
            best_mv = move
        alpha = max(alpha, best_eval)
    return best_mv

def render_board_to_png(board):
    svg_data = chess.svg.board(board=board, size=512)
    return cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))

def play_game(video_name="chess_game_AlphaBeta.mp4"):
    env = gym.make("Chess-v0")
    obs = env.reset()
    board = env._board
    done = False

    writer = imageio.get_writer(video_name, fps=1)  # 1 frame per second

    while not done:
        png_bytes = render_board_to_png(board.copy())
        writer.append_data(imageio.v2.imread(png_bytes, format='png'))

        if board.turn == chess.BLACK:
            move = best_move(board, 3)  # Black searches 4-ply
            print(f"Black move: {move}")
        else:
            move = best_move(board, 2)  # White searches 3-ply
            print(f"White move: {move}")

        if move is None:
            break

        obs, reward, done, info = env.step(move)
        png_bytes = render_board_to_png(board.copy())
        writer.append_data(imageio.v2.imread(png_bytes, format='png'))

        if board.is_game_over():
            print(env._board.result())
            break

    writer.close()
    env.close()
    print(f"Video saved as {video_name}")

if __name__ == "__main__":
    play_game()
