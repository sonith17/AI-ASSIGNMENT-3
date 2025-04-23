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

def evaluate(board):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    score += 0.1 * len(list(board.legal_moves)) if board.turn == chess.WHITE else -0.1 * len(list(board.legal_moves))
    return score
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
