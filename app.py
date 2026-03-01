import streamlit as st
import random
import time
import json
import os
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Peppa Pig Memory Game 🐷",
    page_icon="🐷",
    layout="centered",
)

# ── Leaderboard file ──────────────────────────────────────────────────────────
SCORES_FILE = "peppa_scores.json"

def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return []

def save_score(name, difficulty, mode, moves, pairs, date):
    scores = load_scores()
    scores.append({
        "name": name,
        "difficulty": difficulty,
        "mode": mode,
        "moves": moves,
        "pairs": pairs,
        "date": date,
    })
    # Keep best 50 scores
    scores = sorted(scores, key=lambda x: (x["difficulty"] != "Hard", x["difficulty"] != "Medium", x["moves"]))
    scores = scores[:50]
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Baloo 2', cursive;
    background-color: #fff0f5;
}
h1 { font-size: 2.6rem !important; color: #e91e8c !important; text-align: center; }

div.stButton > button {
    font-family: 'Baloo 2', cursive;
    border-radius: 16px;
    border: 3px solid #f9a8d4;
    background: linear-gradient(135deg, #ffd6ec, #fff0fa);
    box-shadow: 0 4px 12px rgba(233,30,140,0.15);
    transition: transform 0.15s, box-shadow 0.15s;
    cursor: pointer; font-weight: 700;
}
div.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 18px rgba(233,30,140,0.25);
    border-color: #e91e8c;
}
div.stButton > button:active { transform: scale(0.96); }

.card-easy   { width:110px; height:110px; font-size:2.8rem; }
.card-medium { width: 90px; height: 90px; font-size:2.2rem; }
.card-hard   { width: 75px; height: 75px; font-size:1.8rem; }

.card-base { border-radius:16px; display:flex; align-items:center; justify-content:center; }
.matched-p1 { border:3px solid #86efac; background:linear-gradient(135deg,#d1fae5,#f0fdf4); box-shadow:0 4px 12px rgba(34,197,94,0.2); }
.matched-p2 { border:3px solid #93c5fd; background:linear-gradient(135deg,#dbeafe,#eff6ff); box-shadow:0 4px 12px rgba(59,130,246,0.2); }
.flipped    { border:3px solid #e91e8c; background:linear-gradient(135deg,#fce7f3,#fdf2f8); box-shadow:0 6px 18px rgba(233,30,140,0.3); }

.score-box    { background:linear-gradient(135deg,#fce7f3,#fdf2f8); border:2px solid #f9a8d4; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; color:#be185d; font-weight:700; font-size:1rem; }
.score-p1     { border:3px solid #e91e8c; background:linear-gradient(135deg,#fce7f3,#fdf2f8); color:#be185d; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; font-weight:700; font-size:1rem; }
.score-p1-off { border:2px dashed #f9a8d4; background:#fdf2f8; color:#f9a8d4; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; font-weight:700; font-size:1rem; }
.score-p2     { border:3px solid #3b82f6; background:linear-gradient(135deg,#dbeafe,#eff6ff); color:#1d4ed8; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; font-weight:700; font-size:1rem; }
.score-p2-off { border:2px dashed #93c5fd; background:#eff6ff; color:#93c5fd; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; font-weight:700; font-size:1rem; }

.turn-banner { border-radius:16px; padding:8px 20px; text-align:center; font-size:1.15rem; font-weight:800; margin:6px 0 10px 0; }
.turn-p1 { background:linear-gradient(135deg,#fce7f3,#fdf2f8); border:2px solid #e91e8c; color:#be185d; }
.turn-p2 { background:linear-gradient(135deg,#dbeafe,#eff6ff); border:2px solid #3b82f6; color:#1d4ed8; }

.badge { display:inline-block; padding:3px 14px; border-radius:999px; font-size:0.85rem; font-weight:800; margin-bottom:6px; }
.badge-easy   { background:#dcfce7; color:#15803d; }
.badge-medium { background:#fef9c3; color:#b45309; }
.badge-hard   { background:#fee2e2; color:#b91c1c; }

.win-banner { background:linear-gradient(135deg,#fce7f3,#bfdbfe); border:3px solid #e91e8c; border-radius:24px; padding:24px; text-align:center; font-size:1.5rem; color:#9d174d; font-weight:800; }

/* Leaderboard table */
.lb-wrap { background:linear-gradient(135deg,#fdf2f8,#eff6ff); border:3px solid #f9a8d4; border-radius:24px; padding:20px; margin-top:12px; }
.lb-title { font-size:1.5rem; font-weight:800; color:#be185d; text-align:center; margin-bottom:12px; }
.lb-row { display:flex; align-items:center; gap:10px; padding:8px 12px; border-radius:14px; margin-bottom:6px; font-weight:700; font-size:0.95rem; }
.lb-row-gold   { background:linear-gradient(135deg,#fef9c3,#fde68a); border:2px solid #f59e0b; color:#92400e; }
.lb-row-silver { background:linear-gradient(135deg,#f1f5f9,#e2e8f0); border:2px solid #94a3b8; color:#475569; }
.lb-row-bronze { background:linear-gradient(135deg,#fef3c7,#fde8c8); border:2px solid #d97706; color:#92400e; }
.lb-row-normal { background:white; border:2px solid #f9a8d4; color:#be185d; }
.lb-rank { font-size:1.3rem; min-width:36px; text-align:center; }
.lb-name { flex:1; }
.lb-detail { font-size:0.8rem; opacity:0.75; }
.lb-moves { font-size:1rem; font-weight:800; min-width:60px; text-align:right; }

.peppa-sub { text-align:center; font-size:1rem; color:#be185d; margin-bottom:4px; }

/* Name input styling */
div[data-testid="stTextInput"] input {
    font-family: 'Baloo 2', cursive !important;
    border-radius: 14px !important;
    border: 3px solid #f9a8d4 !important;
    background: #fdf2f8 !important;
    color: #be185d !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
ALL_EMOJIS = ["🐷","🌈","🌟","🦋","🍭","🐸","🎀","🌸","🎠","🦄","🍀","🎪"]
DIFF_CONFIG = {
    "Easy":   {"pairs":4,  "cols":4, "card_class":"card-easy",   "label":"4 pairs · 8 cards",   "emoji":"🌸", "color":"#22c55e"},
    "Medium": {"pairs":8,  "cols":4, "card_class":"card-medium", "label":"8 pairs · 16 cards",  "emoji":"🌟", "color":"#f59e0b"},
    "Hard":   {"pairs":12, "cols":6, "card_class":"card-hard",   "label":"12 pairs · 24 cards", "emoji":"🔥", "color":"#ef4444"},
}
badge_map = {"Easy":"badge-easy","Medium":"badge-medium","Hard":"badge-hard"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def init_game():
    cfg   = DIFF_CONFIG[st.session_state.difficulty]
    n     = cfg["pairs"]
    cards = ALL_EMOJIS[:n] * 2
    random.shuffle(cards)
    total = n * 2
    st.session_state.cards         = cards
    st.session_state.revealed      = [False] * total
    st.session_state.matched       = [False] * total
    st.session_state.matched_by    = [None]  * total
    st.session_state.flipped       = []
    st.session_state.moves         = 0
    st.session_state.matches       = 0
    st.session_state.lock          = False
    st.session_state.current_player= 1
    st.session_state.score_p1      = 0
    st.session_state.score_p2      = 0
    st.session_state.game_ready    = True
    st.session_state.score_saved   = False
    st.session_state.winner_name   = ""

def go_home():
    for k in ["mode","difficulty","game_ready","score_saved","winner_name"]:
        st.session_state.pop(k, None)

def show_leaderboard(highlight_name=None):
    scores = load_scores()
    if not scores:
        st.markdown('<div style="text-align:center;color:#be185d;font-weight:700;padding:16px">No scores yet — be the first! 🌟</div>', unsafe_allow_html=True)
        return

    medals = {0:"🥇", 1:"🥈", 2:"🥉"}
    row_css = {0:"lb-row-gold", 1:"lb-row-silver", 2:"lb-row-bronze"}

    st.markdown('<div class="lb-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="lb-title">🏆 Hall of Fame 🏆</div>', unsafe_allow_html=True)

    for i, s in enumerate(scores[:10]):
        rank_icon = medals.get(i, f"#{i+1}")
        css       = row_css.get(i, "lb-row-normal")
        diff_icon = DIFF_CONFIG[s["difficulty"]]["emoji"]
        mode_icon = "👥" if s["mode"] == "two" else "👤"
        highlight = "outline: 3px solid #e91e8c;" if highlight_name and s["name"] == highlight_name else ""
        st.markdown(f"""
        <div class="lb-row {css}" style="{highlight}">
            <span class="lb-rank">{rank_icon}</span>
            <span class="lb-name">
                {s['name']}
                <span class="lb-detail">&nbsp;{mode_icon} {diff_icon} {s['difficulty']}</span>
            </span>
            <span class="lb-moves">🎯 {s['moves']}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 1 — Mode selection
# ─────────────────────────────────────────────────────────────────────────────
if "mode" not in st.session_state:
    st.markdown("# 🐷 Peppa's Memory Game")
    st.markdown('<p class="peppa-sub">Choose how you want to play! 🌟</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#fce7f3,#fdf2f8);
             border:3px solid #e91e8c;border-radius:24px;padding:28px 16px;text-align:center;margin:6px;">
            <div style="font-size:3rem">🐷</div>
            <div style="font-size:1.3rem;font-weight:800;color:#be185d;margin:8px 0">Single Player</div>
            <div style="color:#be185d;font-size:0.9rem">Play solo &amp; beat<br>your own score!</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Play Solo", use_container_width=True, key="btn_single"):
            st.session_state.mode = "single"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#dbeafe,#eff6ff);
             border:3px solid #3b82f6;border-radius:24px;padding:28px 16px;text-align:center;margin:6px;">
            <div style="font-size:3rem">🐷🐷</div>
            <div style="font-size:1.3rem;font-weight:800;color:#1d4ed8;margin:8px 0">2 Players</div>
            <div style="color:#1d4ed8;font-size:0.9rem">Take turns &amp; see<br>who finds more pairs!</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Play Together", use_container_width=True, key="btn_two"):
            st.session_state.mode = "two"
            st.rerun()

    # Show leaderboard on home screen too
    st.markdown("<br>", unsafe_allow_html=True)
    show_leaderboard()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 2 — Difficulty selection
# ─────────────────────────────────────────────────────────────────────────────
if "difficulty" not in st.session_state:
    st.markdown("# 🐷 Peppa's Memory Game")
    mode_txt = "👤 Single Player" if st.session_state.mode == "single" else "👥 2 Players"
    st.markdown(f'<p class="peppa-sub">{mode_txt} · Pick your difficulty! 🌟</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    panels = [
        ("Easy",   col1, "#22c55e", "🌸", "#dcfce7", "#15803d", "4 pairs · 8 cards",   "Perfect for little ones!"),
        ("Medium", col2, "#f59e0b", "🌟", "#fef9c3", "#b45309", "8 pairs · 16 cards",  "A fun challenge!"),
        ("Hard",   col3, "#ef4444", "🔥", "#fee2e2", "#b91c1c", "12 pairs · 24 cards", "For memory masters!"),
    ]
    for diff, col, border, icon, bg, fg, sublabel, desc in panels:
        with col:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{bg},{bg}99);
                 border:3px solid {border};border-radius:24px;
                 padding:24px 12px;text-align:center;margin:4px;">
                <div style="font-size:3rem">{icon}</div>
                <div style="font-size:1.2rem;font-weight:800;color:{fg};margin:6px 0">{diff}</div>
                <div style="font-size:0.8rem;color:{fg};font-weight:700;margin-bottom:4px">{sublabel}</div>
                <div style="color:{fg};font-size:0.85rem;opacity:0.85">{desc}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"▶ {diff}", use_container_width=True, key=f"btn_diff_{diff}"):
                st.session_state.difficulty = diff
                init_game()
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back", use_container_width=True):
        go_home()
        st.rerun()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 3 — The Game
# ─────────────────────────────────────────────────────────────────────────────
diff    = st.session_state.difficulty
cfg     = DIFF_CONFIG[diff]
n_pairs = cfg["pairs"]
total   = n_pairs * 2
cols    = cfg["cols"]
n_rows  = total // cols
cclass  = cfg["card_class"]

st.markdown("# 🐷 Peppa's Memory Game")
mode_label = "👤 Single Player" if st.session_state.mode == "single" else "👥 2 Players"
st.markdown(
    f'<p class="peppa-sub">{mode_label} &nbsp;·&nbsp;'
    f'<span class="badge {badge_map[diff]}">{cfg["emoji"]} {diff}</span></p>',
    unsafe_allow_html=True,
)

# ── Scoreboard row ────────────────────────────────────────────────────────────
if st.session_state.mode == "single":
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="score-box">🎯 Moves<br>{st.session_state.moves}</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="score-box">💖 Matches<br>{st.session_state.matches} / {n_pairs}</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="score-box">🃏 Left<br>{total - st.session_state.matches*2}</div>', unsafe_allow_html=True)
else:
    p1_active = st.session_state.current_player == 1
    c1, cmid, c2 = st.columns([2,1,2])
    with c1:
        css   = "score-p1" if p1_active else "score-p1-off"
        arrow = " ◀ TURN" if p1_active else ""
        st.markdown(f'<div class="{css}">🌸 Player 1{arrow}<br>{st.session_state.score_p1} pairs</div>', unsafe_allow_html=True)
    with cmid:
        st.markdown(f'<div class="score-box">🎯 Moves<br>{st.session_state.moves}</div>', unsafe_allow_html=True)
    with c2:
        css   = "score-p2" if not p1_active else "score-p2-off"
        arrow = " ◀ TURN" if not p1_active else ""
        st.markdown(f'<div class="{css}">🦋 Player 2{arrow}<br>{st.session_state.score_p2} pairs</div>', unsafe_allow_html=True)

    if st.session_state.current_player == 1:
        st.markdown('<div class="turn-banner turn-p1">🌸 Player 1\'s turn — flip two cards!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="turn-banner turn-p2">🦋 Player 2\'s turn — flip two cards!</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Win / End check ───────────────────────────────────────────────────────────
if st.session_state.matches == n_pairs:

    # Determine winner info for leaderboard
    if st.session_state.mode == "single":
        winner_label = "You"
        st.markdown(f"""
        <div class="win-banner">
            🎉 Woohoo! You won! 🎉<br>
            <span style="font-size:1rem;font-weight:400">All {n_pairs} pairs in <b>{st.session_state.moves}</b> moves on <b>{diff}</b>!</span><br>
            🐷🌈🌟🦋🍭🐸🎀🌸
        </div>""", unsafe_allow_html=True)
    else:
        s1, s2 = st.session_state.score_p1, st.session_state.score_p2
        if s1 > s2:
            result, color, winner_label = f"🌸 Player 1 wins with {s1} pairs! 🎉", "#be185d", "Player 1"
        elif s2 > s1:
            result, color, winner_label = f"🦋 Player 2 wins with {s2} pairs! 🎉", "#1d4ed8", "Player 2"
        else:
            result, color, winner_label = f"🤝 It's a tie! {s1} pairs each!", "#7c3aed", "Both players"
        st.markdown(f"""
        <div class="win-banner" style="border-color:{color};color:{color}">
            🎉 Game Over! 🎉<br>
            <span style="font-size:1.1rem">{result}</span><br>
            <span style="font-size:0.9rem;font-weight:400">🌸 P1: {s1} &nbsp;|&nbsp; 🦋 P2: {s2} &nbsp;·&nbsp; {diff}</span><br>
            🐷🌈🌟🦋🍭🐸🎀🌸
        </div>""", unsafe_allow_html=True)

    st.balloons()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Name entry & save ──────────────────────────────────────────────────────
    if not st.session_state.get("score_saved", False):
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#fef9c3,#fce7f3);border:2px solid #f59e0b;
             border-radius:20px;padding:16px;text-align:center;margin-bottom:12px;">
            <div style="font-size:1.1rem;font-weight:800;color:#92400e">
                🏆 {winner_label} — enter your name for the Hall of Fame!
            </div>
        </div>""", unsafe_allow_html=True)

        name_input = st.text_input(
            "",
            placeholder="Type your name here... 🌟",
            max_chars=20,
            key="name_field",
            label_visibility="collapsed",
        )

        if st.button("✅ Save my score!", use_container_width=True):
            name = name_input.strip() or "Anonymous 🐷"
            save_score(
                name       = name,
                difficulty = diff,
                mode       = st.session_state.mode,
                moves      = st.session_state.moves,
                pairs      = n_pairs,
                date       = datetime.now().strftime("%d %b %Y"),
            )
            st.session_state.score_saved  = True
            st.session_state.winner_name  = name
            st.rerun()
    else:
        saved_name = st.session_state.get("winner_name", "")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#dcfce7,#d1fae5);border:2px solid #22c55e;
             border-radius:20px;padding:12px;text-align:center;margin-bottom:12px;">
            <div style="font-size:1rem;font-weight:800;color:#15803d">
                ✅ Score saved for <b>{saved_name}</b>! Great job! 🌟
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Leaderboard ───────────────────────────────────────────────────────────
    show_leaderboard(highlight_name=st.session_state.get("winner_name"))

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb, cc = st.columns(3)
    with ca:
        if st.button("🔄 Play Again", use_container_width=True):
            init_game()
            st.rerun()
    with cb:
        if st.button("🎯 Change Difficulty", use_container_width=True):
            st.session_state.pop("difficulty", None)
            st.session_state.pop("game_ready", None)
            st.session_state.pop("score_saved", None)
            st.rerun()
    with cc:
        if st.button("🏠 Main Menu", use_container_width=True):
            go_home()
            st.rerun()
    st.stop()

# ── Card flip logic ───────────────────────────────────────────────────────────
def flip_card(idx):
    if st.session_state.lock:            return
    if st.session_state.matched[idx]:   return
    if st.session_state.revealed[idx]:  return
    if idx in st.session_state.flipped: return

    st.session_state.revealed[idx] = True
    st.session_state.flipped.append(idx)

    if len(st.session_state.flipped) == 2:
        st.session_state.moves += 1
        i, j = st.session_state.flipped
        if st.session_state.cards[i] == st.session_state.cards[j]:
            st.session_state.matched[i]    = True
            st.session_state.matched[j]    = True
            st.session_state.matched_by[i] = st.session_state.current_player
            st.session_state.matched_by[j] = st.session_state.current_player
            st.session_state.matches       += 1
            if st.session_state.mode == "two":
                if st.session_state.current_player == 1:
                    st.session_state.score_p1 += 1
                else:
                    st.session_state.score_p2 += 1
            st.session_state.flipped = []
        else:
            st.session_state.lock = True

# ── Grid ──────────────────────────────────────────────────────────────────────
grid_rows = [st.columns(cols) for _ in range(n_rows)]

for i in range(total):
    r = i // cols
    c = i % cols
    with grid_rows[r][c]:
        if st.session_state.matched[i]:
            by  = st.session_state.matched_by[i]
            mcl = "matched-p2" if by == 2 else "matched-p1"
            st.markdown(f'<div class="card-base {cclass} {mcl}">{st.session_state.cards[i]}</div>', unsafe_allow_html=True)
        elif st.session_state.revealed[i]:
            st.markdown(f'<div class="card-base {cclass} flipped">{st.session_state.cards[i]}</div>', unsafe_allow_html=True)
        else:
            if st.button("🐷", key=f"card_{i}"):
                flip_card(i)
                st.rerun()

# ── Unmatched pair — flip back, switch player ─────────────────────────────────
if st.session_state.lock and len(st.session_state.flipped) == 2:
    time.sleep(0.9)
    i, j = st.session_state.flipped
    st.session_state.revealed[i] = False
    st.session_state.revealed[j] = False
    st.session_state.flipped     = []
    st.session_state.lock        = False
    if st.session_state.mode == "two":
        st.session_state.current_player = 2 if st.session_state.current_player == 1 else 1
    st.rerun()

# ── Bottom nav ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
ca, cb, cc = st.columns(3)
with ca:
    if st.button("🔄 New Game", use_container_width=True):
        init_game()
        st.rerun()
with cb:
    if st.button("🎯 Difficulty", use_container_width=True):
        st.session_state.pop("difficulty", None)
        st.session_state.pop("game_ready", None)
        st.rerun()
with cc:
    if st.button("🏠 Menu", use_container_width=True):
        go_home()
        st.rerun()
