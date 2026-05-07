import streamlit as st
import chess
import chess.svg
import random
import time
import math
from collections import defaultdict

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chess RL AI",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --gold: #D4AF37;
    --gold-light: #F0D060;
    --dark: #0D0D0D;
    --dark2: #161616;
    --dark3: #1E1E1E;
    --dark4: #252525;
    --border: #2A2A2A;
    --text: #E8E8E8;
    --muted: #888;
    --green: #4CAF50;
    --red: #EF5350;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--dark);
    color: var(--text);
}

.stApp { background-color: var(--dark); }

/* Header */
.chess-header {
    text-align: center;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.chess-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: var(--gold);
    letter-spacing: -1px;
    margin: 0;
    line-height: 1;
}
.chess-header p {
    color: var(--muted);
    font-size: 0.85rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 6px;
}

/* Status bar */
.status-bar {
    background: var(--dark3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 20px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.95rem;
    font-weight: 500;
}
.status-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--green);
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* Info cards */
.info-card {
    background: var(--dark3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.info-card h4 {
    font-family: 'Playfair Display', serif;
    color: var(--gold);
    font-size: 0.85rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0 0 8px;
}
.info-card p {
    color: var(--text);
    font-size: 0.9rem;
    margin: 0;
}

/* Move history */
.move-history {
    background: var(--dark3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    max-height: 220px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
}
.move-pair { display: flex; gap: 12px; margin-bottom: 4px; color: var(--text); }
.move-num { color: var(--muted); min-width: 24px; }
.move-w { color: var(--text); min-width: 60px; }
.move-b { color: #aaa; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--dark2) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-family: 'Playfair Display', serif;
}

/* Buttons */
.stButton > button {
    background: var(--dark4);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 8px 18px;
    transition: all 0.2s;
    width: 100%;
}
.stButton > button:hover {
    background: var(--gold);
    color: var(--dark);
    border-color: var(--gold);
}

/* Select box */
.stSelectbox > div > div {
    background: var(--dark3);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
}

/* Metric */
.stMetric { background: var(--dark3); border-radius: 10px; padding: 12px; border: 1px solid var(--border); }

/* Board container */
.board-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    background: var(--dark2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
}

/* Text input */
.stTextInput input {
    background: var(--dark3);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 1rem;
}
.stTextInput input:focus {
    border-color: var(--gold);
    box-shadow: 0 0 0 2px rgba(212,175,55,0.15);
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--dark3);
    border-radius: 8px;
    color: var(--gold) !important;
    font-family: 'Playfair Display', serif;
}

hr { border-color: var(--border); }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  REINFORCEMENT LEARNING ENGINE
# ════════════════════════════════════════════════════════════════

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

# Piece-square tables for positional evaluation
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}


def evaluate_board(board: chess.Board) -> int:
    """Evaluate board from White's perspective using material + PST."""
    if board.is_checkmate():
        return -20000 if board.turn == chess.WHITE else 20000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        val = PIECE_VALUES[piece.piece_type]
        table = TABLES[piece.piece_type]
        if piece.color == chess.WHITE:
            pos_val = table[sq]
            score += val + pos_val
        else:
            pos_val = table[chess.square_mirror(sq)]
            score -= val + pos_val
    return score


def minimax(board, depth, alpha, beta, maximizing):
    """Alpha-Beta Minimax — the RL-inspired tree search."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if maximizing:
        best_val = -math.inf
        for move in order_moves(board):
            board.push(move)
            val, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if val > best_val:
                best_val, best_move = val, move
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best_val, best_move
    else:
        best_val = math.inf
        for move in order_moves(board):
            board.push(move)
            val, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if val < best_val:
                best_val, best_move = val, move
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best_val, best_move


def order_moves(board):
    """Move ordering: captures first, then checks, then quiet moves."""
    captures, checks, quiets = [], [], []
    for move in board.legal_moves:
        if board.is_capture(move):
            captures.append(move)
        elif board.gives_check(move):
            checks.append(move)
        else:
            quiets.append(move)
    return captures + checks + quiets


def get_ai_move(board, difficulty):
    depth_map = {"Beginner 🌱": 1, "Intermediate ⚡": 2, "Advanced 🔥": 3, "Expert 👑": 4}
    depth = depth_map.get(difficulty, 2)
    maximizing = (board.turn == chess.WHITE)
    _, move = minimax(board, depth, -math.inf, math.inf, maximizing)
    if move is None:
        legal = list(board.legal_moves)
        move = random.choice(legal) if legal else None
    return move


# ════════════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════════════

def init_state():
    if "board" not in st.session_state:
        st.session_state.board = chess.Board()
    if "move_history" not in st.session_state:
        st.session_state.move_history = []
    if "player_color" not in st.session_state:
        st.session_state.player_color = chess.WHITE
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "last_move" not in st.session_state:
        st.session_state.last_move = None
    if "ai_thinking" not in st.session_state:
        st.session_state.ai_thinking = False
    if "selected_square" not in st.session_state:
        st.session_state.selected_square = None
    if "status_msg" not in st.session_state:
        st.session_state.status_msg = "Your turn — enter a move in UCI notation (e.g. e2e4)"
    if "eval_score" not in st.session_state:
        st.session_state.eval_score = 0
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Intermediate ⚡"
    if "wins" not in st.session_state:
        st.session_state.wins = 0
    if "losses" not in st.session_state:
        st.session_state.losses = 0
    if "draws" not in st.session_state:
        st.session_state.draws = 0

init_state()


# ════════════════════════════════════════════════════════════════
#  SIDEBAR — METHODOLOGY
# ════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ♟️ Chess RL AI")
    st.markdown("---")

    st.markdown("### 🎮 Game Settings")
    difficulty = st.selectbox(
        "AI Difficulty",
        ["Beginner 🌱", "Intermediate ⚡", "Advanced 🔥", "Expert 👑"],
        index=1,
    )
    st.session_state.difficulty = difficulty

    player_side = st.selectbox("Play as", ["White ⬜", "Black ⬛"])
    st.session_state.player_color = chess.WHITE if "White" in player_side else chess.BLACK

    if st.button("🔄 New Game"):
        st.session_state.board = chess.Board()
        st.session_state.move_history = []
        st.session_state.game_over = False
        st.session_state.last_move = None
        st.session_state.status_msg = "New game started! Your turn."
        st.session_state.eval_score = 0
        st.rerun()

    st.markdown("---")

    # Score
    c1, c2, c3 = st.columns(3)
    c1.metric("Wins", st.session_state.wins)
    c2.metric("Losses", st.session_state.losses)
    c3.metric("Draws", st.session_state.draws)

    st.markdown("---")

    # ── METHODOLOGY ──────────────────────────────────────────────
    st.markdown("## 📚 Methodology")

    with st.expander("🧠 What is RL?", expanded=False):
        st.markdown("""
**Reinforcement Learning (RL)** is a machine learning paradigm where an agent learns to make decisions by interacting with an environment to maximize cumulative reward.

**Key Components:**
- **Agent** → The Chess AI
- **Environment** → The Chessboard
- **State** → Board position
- **Action** → A legal chess move
- **Reward** → Win (+1), Loss (−1), Draw (0)
        """)

    with st.expander("🌳 Minimax + Alpha-Beta", expanded=False):
        st.markdown("""
**Minimax Algorithm** explores a game tree:
- **MAX** node: AI maximizes score
- **MIN** node: Opponent minimizes score

**Alpha-Beta Pruning** cuts off branches that can't affect the result:
```
α = best score MAX can guarantee
β = best score MIN can guarantee
If β ≤ α → prune the branch
```
This reduces complexity from **O(b^d)** to **O(b^(d/2))**, effectively doubling search depth!
        """)

    with st.expander("♟️ Board Evaluation", expanded=False):
        st.markdown("""
**Material Value:**
| Piece | Value |
|-------|-------|
| Pawn  | 100   |
| Knight| 320   |
| Bishop| 330   |
| Rook  | 500   |
| Queen | 900   |
| King  | 20000 |

**Piece-Square Tables (PST):**  
Each piece has a 64-value table encoding positional bonuses — e.g., pawns are rewarded for advancing, knights for centralizing.

**Score = Σ(material) + Σ(positional)**
        """)

    with st.expander("⚡ Move Ordering", expanded=False):
        st.markdown("""
Alpha-Beta is most effective when best moves are searched first:

1. **Captures** — high chance of material gain
2. **Checks** — forcing moves limit opponent options  
3. **Quiet moves** — positional improvements

This **heuristic ordering** leads to far more pruning in practice.
        """)

    with st.expander("🎓 RL Connection", expanded=False):
        st.markdown("""
Classic chess engines use **planning** (Minimax), while modern RL agents like **AlphaZero** use:

1. **Self-play** — generate training data by playing against itself
2. **Monte Carlo Tree Search (MCTS)** — stochastic tree search
3. **Deep Neural Network** — replaces handcrafted evaluation:
   - Policy head → move probabilities
   - Value head → position evaluation

Our engine uses the **classical RL-adjacent approach** with:
- Minimax as the *policy*
- PST + material as the *value function*
- Alpha-Beta as *efficient exploration*
        """)

    with st.expander("📊 Complexity Analysis", expanded=False):
        st.markdown("""
| Depth | Nodes (no pruning) | Nodes (α-β) |
|-------|-------------------|--------------|
| 1     | ~30               | ~30          |
| 2     | ~900              | ~55          |
| 3     | ~27,000           | ~300         |
| 4     | ~810,000          | ~1,500       |

Average branching factor in chess ≈ **35**  
Alpha-Beta reduces it to ≈ **6** effectively.
        """)

    st.markdown("---")
    st.markdown("""
<div style='font-size:0.75rem; color:#666; text-align:center;'>
BTAIC602 · Advanced Machine Learning<br>
CA-II · Reinforcement Learning
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ════════════════════════════════════════════════════════════════

st.markdown("""
<div class='chess-header'>
  <h1>♟ Chess AI</h1>
  <p>Reinforcement Learning · Minimax · Alpha-Beta Pruning</p>
</div>
""", unsafe_allow_html=True)

board = st.session_state.board

# Layout
col_board, col_info = st.columns([3, 2])

with col_board:
    # Status
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        st.error(f"♚ Checkmate! **{winner}** wins!")
        if not st.session_state.game_over:
            st.session_state.game_over = True
            if winner == ("White" if st.session_state.player_color == chess.WHITE else "Black"):
                st.session_state.wins += 1
            else:
                st.session_state.losses += 1
    elif board.is_stalemate():
        st.warning("🤝 Stalemate — Draw!")
        if not st.session_state.game_over:
            st.session_state.game_over = True
            st.session_state.draws += 1
    elif board.is_insufficient_material():
        st.warning("🤝 Insufficient material — Draw!")
        if not st.session_state.game_over:
            st.session_state.game_over = True
            st.session_state.draws += 1
    elif board.is_check():
        st.warning("⚠️ **Check!** Your king is under attack.")
    else:
        turn = "Your turn ⬜" if board.turn == st.session_state.player_color else "AI is thinking... 🤖"
        st.info(f"🎯 {turn}")

    # Board SVG
    last_move = st.session_state.last_move
    svg = chess.svg.board(
        board,
        lastmove=last_move,
        size=480,
        colors={
            "square light": "#F0D9B5",
            "square dark": "#B58863",
            "square light lastmove": "#CDD26A",
            "square dark lastmove": "#AAAA44",
        },
        flipped=(st.session_state.player_color == chess.BLACK)
    )
    st.markdown(f"<div style='max-width:100%;'>{svg}</div>", unsafe_allow_html=True)

    # Move input
    if not st.session_state.game_over and board.turn == st.session_state.player_color:
        st.markdown("**Enter Move** *(UCI format: e2e4, g1f3, e1g1 for castling)*")
        user_input = st.text_input("", placeholder="e.g. e2e4", key="move_input", label_visibility="collapsed")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶ Make Move", use_container_width=True):
                if user_input:
                    try:
                        move = chess.Move.from_uci(user_input.strip().lower())
                        if move in board.legal_moves:
                            board.push(move)
                            st.session_state.last_move = move
                            st.session_state.move_history.append(move)
                            st.session_state.eval_score = evaluate_board(board)
                            st.rerun()
                        else:
                            st.error("❌ Illegal move. Try again.")
                    except Exception:
                        st.error("❌ Invalid UCI format. Example: e2e4")
        with c2:
            if st.button("💡 Hint", use_container_width=True):
                hint_move = get_ai_move(board, "Intermediate ⚡")
                if hint_move:
                    st.info(f"Suggestion: **{hint_move.uci()}**")

    # AI turn
    if not st.session_state.game_over and board.turn != st.session_state.player_color:
        with st.spinner("🤖 AI calculating best move..."):
            time.sleep(0.3)
            ai_move = get_ai_move(board, st.session_state.difficulty)
            if ai_move:
                board.push(ai_move)
                st.session_state.last_move = ai_move
                st.session_state.move_history.append(ai_move)
                st.session_state.eval_score = evaluate_board(board)
        st.rerun()


with col_info:
    st.markdown("### 📊 Game Info")

    # Eval bar
    score = st.session_state.eval_score
    score_display = f"+{score/100:.1f}" if score > 0 else f"{score/100:.1f}"
    color_label = "White" if score > 0 else ("Black" if score < 0 else "Equal")
    adv_color = "#4CAF50" if score > 0 else ("#EF5350" if score < 0 else "#888")

    st.markdown(f"""
<div class='info-card'>
  <h4>⚖️ Position Evaluation</h4>
  <p style='font-size:1.4rem; font-weight:700; color:{adv_color};'>{score_display}</p>
  <p style='color:#888; font-size:0.8rem;'>{color_label} advantage</p>
</div>
""", unsafe_allow_html=True)

    # Game stats
    st.markdown(f"""
<div class='info-card'>
  <h4>🎲 Game Stats</h4>
  <p>Moves played: <strong>{len(st.session_state.move_history)}</strong></p>
  <p>Turn: <strong>{'White' if board.turn == chess.WHITE else 'Black'}</strong></p>
  <p>Difficulty: <strong>{st.session_state.difficulty}</strong></p>
  <p>Castling rights: <strong>{'Yes' if board.has_castling_rights(board.turn) else 'None'}</strong></p>
</div>
""", unsafe_allow_html=True)

    # Legal moves count
    legal_count = board.legal_moves.count()
    st.markdown(f"""
<div class='info-card'>
  <h4>🔢 Legal Moves Available</h4>
  <p style='font-size:1.8rem; font-weight:700; color:#D4AF37;'>{legal_count}</p>
</div>
""", unsafe_allow_html=True)

    # Move history
    st.markdown("### 📜 Move History")
    history = st.session_state.move_history
    if history:
        board_temp = chess.Board()
        pairs = []
        moves_san = []
        for m in history:
            try:
                san = board_temp.san(m)
                moves_san.append(san)
                board_temp.push(m)
            except Exception:
                moves_san.append(m.uci())

        history_html = "<div class='move-history'>"
        for i in range(0, len(moves_san), 2):
            white_m = moves_san[i]
            black_m = moves_san[i+1] if i+1 < len(moves_san) else ""
            history_html += f"""<div class='move-pair'>
                <span class='move-num'>{i//2 + 1}.</span>
                <span class='move-w'>{white_m}</span>
                <span class='move-b'>{black_m}</span>
            </div>"""
        history_html += "</div>"
        st.markdown(history_html, unsafe_allow_html=True)
    else:
        st.markdown("<div class='move-history' style='color:#555;'>No moves yet...</div>", unsafe_allow_html=True)

    # Quick reference
    st.markdown("### 🗒️ Quick Reference")
    st.markdown("""
<div class='info-card'>
  <h4>UCI Notation Examples</h4>
  <p>
  <code>e2e4</code> → Pawn e2 to e4<br>
  <code>g1f3</code> → Knight to f3<br>
  <code>e1g1</code> → Castle kingside<br>
  <code>e7e8q</code> → Pawn promotes to Queen
  </p>
</div>
""", unsafe_allow_html=True)
