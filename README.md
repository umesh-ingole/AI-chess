# ♟️ Chess RL AI — BTAIC602 CA-II

**Advanced Machine Learning | Reinforcement Learning Project**

A fully playable Chess AI built using Reinforcement Learning concepts:
- **Minimax Algorithm** with Alpha-Beta Pruning
- **Piece-Square Tables** for positional evaluation
- **Move Ordering** heuristics (captures → checks → quiet)
- **Material + Positional** board evaluation function

---

## 🚀 Deploy to Streamlit Cloud (Global Link)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Chess RL AI - CA-II"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/chess-rl-ai.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to **https://share.streamlit.io**
2. Click **"New app"**
3. Select your GitHub repo
4. Set **Main file path** → `app.py`
5. Click **Deploy** ✅

Your global link will be:  
`https://YOUR_USERNAME-chess-rl-ai-app-XXXXX.streamlit.app`

---

## 🖥️ Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📚 Methodology (in Sidebar)

| Section | Content |
|---------|---------|
| What is RL? | Agent, Environment, State, Action, Reward |
| Minimax + Alpha-Beta | Tree search, pruning, complexity |
| Board Evaluation | Material values, PST |
| Move Ordering | Captures, checks, quiet moves |
| RL Connection | AlphaZero comparison |
| Complexity Analysis | Nodes explored at each depth |

---

## 🎮 How to Play

- Enter moves in **UCI notation**: `e2e4`, `g1f3`, `e1g1` (castle), `e7e8q` (promote)
- Choose difficulty: Beginner / Intermediate / Advanced / Expert
- Play as White or Black
- Use the **Hint** button if stuck

---

*BTAIC602 · Advanced Machine Learning · CA-II · Reinforcement Learning*
