### Evaluation Function
```python
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
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

```


#### **1. Material Balance**
- Each piece is assigned a value:
  - Pawn = 100  
  - Knight = 320  
  - Bishop = 330  
  - Rook = 500  
  - Queen = 900  
  - King = 0 (not scored directly)
- White piece values are **added**, Black's are **subtracted** from the total score.
- This reflects which player has more valuable pieces on the board.

---

#### **2. Mobility Bonus**
- Adds a small bonus based on the number of **legal moves**:
  - `+0.1 × moves` for White's turn  
  - `−0.1 × moves` for Black's turn
- Encourages positions with more options and better flexibility.

---

#### **Interpretation**
- **Positive score** → Favorable for **White**  
- **Negative score** → Favorable for **Black**

---
