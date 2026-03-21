import streamlit as st
import random
import time
import json
import os
import re
import hmac
import hashlib
import math
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# ── Environment variables ─────────────────────────────────────────────────────
load_dotenv()

SECRET_KEY   = os.getenv("PEPPA_SECRET_KEY", "change-me-to-a-random-secret")
RATE_LIMIT   = int(os.getenv("PEPPA_RATE_LIMIT", "3"))
MAX_SCORES   = int(os.getenv("PEPPA_MAX_SCORES", "50"))
SCORES_FILE  = os.getenv("PEPPA_SCORES_FILE", "peppa_scores.json")

if SECRET_KEY == "change-me-to-a-random-secret":
    import warnings
    warnings.warn(
        "⚠️  PEPPA_SECRET_KEY is not set. Copy .env.example to .env and set a real key.",
        stacklevel=2,
    )

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Peppa Pig Memory Game 🐷",
    page_icon="🐷",
    layout="centered",
)

# ════════════════════════════════════════════════════════════════════════════════
# ASSET MANAGER
# ════════════════════════════════════════════════════════════════════════════════

ASSETS_DIR     = Path(__file__).parent / "assets"
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg"}

EMOJI_FALLBACK = {
    "peppa":   "🐷", "george": "🦕", "mama":    "👩",
    "papa":    "👨", "suzy":   "🐑", "danny":   "🐶",
    "rebecca": "🐰", "zoe":    "🦓", "pedro":   "🐴",
    "emily":   "🐘", "default": "⭐",
}

def _to_base64(path: Path) -> str:
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext  = path.suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else "png"
    return f"data:image/{mime};base64,{data}"

def load_sprites() -> list:
    """Scan assets/ map en laad alle afbeeldingen als sprite-dicts."""
    if not ASSETS_DIR.exists():
        return []
    sprites = []
    for file in sorted(ASSETS_DIR.iterdir()):
        if file.suffix.lower() not in SUPPORTED_EXTS:
            continue
        name = file.stem.lower()
        sprites.append({
            "name":  name,
            "label": name.capitalize(),
            "emoji": EMOJI_FALLBACK.get(name, EMOJI_FALLBACK["default"]),
            "b64":   _to_base64(file),
        })
    return sprites

# Laad sprites eenmalig
SPRITES    = load_sprites()
USE_SPRITES = len(SPRITES) >= 2

ALL_EMOJIS = ["🐷","🌈","🌟","🦋","🍭","🐸","🎀","🌸","🎠","🦄","🍀","🎪"]

def render_card_face(card, size_px: int = 80) -> str:
    """Geeft HTML terug voor de voorkant van een kaartje."""
    if isinstance(card, dict) and card.get("b64"):
        return (
            f'<img src="{card["b64"]}" '
            f'style="width:{size_px}px;height:{size_px}px;'
            f'object-fit:contain;border-radius:8px;" '
            f'alt="{card["label"]}">'
        )
    return str(card) if not isinstance(card, dict) else card.get("emoji", "⭐")

# ════════════════════════════════════════════════════════════════════════════════
# 1. INPUT SANITIZATION
# ════════════════════════════════════════════════════════════════════════════════

_NAME_PATTERN = re.compile(r"[^\w\s\-\'\.\!\?éèêëàâùûüôîïç]", re.UNICODE)
_MAX_NAME_LEN = 20

def sanitize_name(raw: str) -> str:
    name = raw.strip()
    name = _NAME_PATTERN.sub("", name)
    name = re.sub(r"\s+", " ", name).strip()
    name = name[:_MAX_NAME_LEN]
    return name or "Anonymous 🐷"


# ════════════════════════════════════════════════════════════════════════════════
# 2. SECURE SCORE STORAGE
# ════════════════════════════════════════════════════════════════════════════════

def _sign(payload: str) -> str:
    return hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()

def _scores_to_payload(scores: list) -> str:
    return json.dumps(scores, sort_keys=True, separators=(",", ":"))

def load_scores() -> list:
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        stored_sig = data.get("sig", "")
        scores     = data.get("scores", [])
        expected   = _sign(_scores_to_payload(scores))
        if not hmac.compare_digest(stored_sig, expected):
            st.warning("⚠️ Leaderboard file was modified externally and has been reset.")
            return []
        validated = []
        for s in scores:
            if (
                isinstance(s.get("name"), str)
                and s.get("difficulty") in ("Easy", "Medium", "Hard")
                and s.get("mode") in ("single", "two")
                and isinstance(s.get("moves"), int) and s["moves"] > 0
                and isinstance(s.get("pairs"), int)
            ):
                validated.append(s)
        return validated
    except Exception:
        return []

def save_score(name: str, difficulty: str, mode: str, moves: int, pairs: int, date: str):
    scores = load_scores()
    scores.append({"name": name, "difficulty": difficulty, "mode": mode,
                   "moves": moves, "pairs": pairs, "date": date})
    order = {"Hard": 0, "Medium": 1, "Easy": 2}
    scores.sort(key=lambda x: (order.get(x["difficulty"], 9), x["moves"]))
    scores  = scores[:MAX_SCORES]
    payload = _scores_to_payload(scores)
    sig     = _sign(payload)
    data    = {"scores": scores, "sig": sig}
    tmp     = SCORES_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, SCORES_FILE)


# ════════════════════════════════════════════════════════════════════════════════
# 3. RATE LIMITING
# ════════════════════════════════════════════════════════════════════════════════

def _can_save_score() -> bool:
    return st.session_state.get("saves_this_session", 0) < RATE_LIMIT

def _record_save():
    st.session_state["saves_this_session"] = st.session_state.get("saves_this_session", 0) + 1


# ════════════════════════════════════════════════════════════════════════════════
# STYLING
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Baloo 2', cursive; background-color: #fff0f5; }
h1 { font-size: 2.6rem !important; color: #e91e8c !important; text-align: center; }

div.stButton > button {
    font-family:'Baloo 2',cursive; border-radius:16px; border:3px solid #f9a8d4;
    background:linear-gradient(135deg,#ffd6ec,#fff0fa);
    box-shadow:0 4px 12px rgba(233,30,140,0.15);
    transition:transform 0.15s,box-shadow 0.15s; cursor:pointer; font-weight:700;
}
div.stButton > button:hover { transform:scale(1.05); box-shadow:0 6px 18px rgba(233,30,140,0.25); border-color:#e91e8c; }
div.stButton > button:active { transform:scale(0.96); }

.card-easy   { width:110px; height:110px; font-size:2.8rem; }
.card-medium { width: 90px; height: 90px; font-size:2.2rem; }
.card-hard   { width: 75px; height: 75px; font-size:1.8rem; }
.card-base { border-radius:16px; display:flex; align-items:center; justify-content:center; overflow:hidden; }
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
.asset-info { background:linear-gradient(135deg,#fef9c3,#fce7f3); border:2px solid #f59e0b; border-radius:16px; padding:10px 16px; text-align:center; font-size:0.9rem; color:#92400e; font-weight:700; margin-bottom:12px; }
div[data-testid="stTextInput"] input {
    font-family:'Baloo 2',cursive !important; border-radius:14px !important;
    border:3px solid #f9a8d4 !important; background:#fdf2f8 !important;
    color:#be185d !important; font-size:1.1rem !important; font-weight:700 !important; text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ── Game config ───────────────────────────────────────────────────────────────
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
    total = n * 2

    if USE_SPRITES:
        # Herhaal pool als er meer paren nodig zijn dan sprites
        repeats = math.ceil(n / len(SPRITES))
        pool    = (SPRITES * repeats)[:n]
        cards   = pool + pool
        random.shuffle(cards)
    else:
        cards = ALL_EMOJIS[:n] * 2
        random.shuffle(cards)

    st.session_state.update(dict(
        cards=cards, revealed=[False]*total, matched=[False]*total,
        matched_by=[None]*total, flipped=[], moves=0, matches=0,
        lock=False, current_player=1, score_p1=0, score_p2=0,
        game_ready=True, score_saved=False, winner_name="",
        use_sprites=USE_SPRITES,
    ))

def go_home():
    for k in ["mode","difficulty","game_ready","score_saved","winner_name"]:
        st.session_state.pop(k, None)

def show_leaderboard(highlight_name=None):
    scores = load_scores()
    if not scores:
        st.markdown('<div style="text-align:center;color:#be185d;font-weight:700;padding:16px">No scores yet — be the first! 🌟</div>', unsafe_allow_html=True)
        return
    medals  = {0:"🥇", 1:"🥈", 2:"🥉"}
    row_css = {0:"lb-row-gold", 1:"lb-row-silver", 2:"lb-row-bronze"}
    st.markdown('<div class="lb-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="lb-title">🏆 Hall of Fame 🏆</div>', unsafe_allow_html=True)
    for i, s in enumerate(scores[:10]):
        rank_icon = medals.get(i, f"#{i+1}")
        css       = row_css.get(i, "lb-row-normal")
        diff_icon = DIFF_CONFIG[s["difficulty"]]["emoji"]
        mode_icon = "👥" if s["mode"] == "two" else "👤"
        highlight = "outline:3px solid #e91e8c;" if highlight_name and s["name"] == highlight_name else ""
        st.markdown(f"""
        <div class="lb-row {css}" style="{highlight}">
            <span class="lb-rank">{rank_icon}</span>
            <span class="lb-name">{s['name']}<span class="lb-detail">&nbsp;{mode_icon} {diff_icon} {s['difficulty']}</span></span>
            <span class="lb-moves">🎯 {s['moves']}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Card flip logic ───────────────────────────────────────────────────────────
def flip_card(idx):
    if st.session_state.lock or st.session_state.matched[idx] or st.session_state.revealed[idx] or idx in st.session_state.flipped:
        return
    st.session_state.revealed[idx] = True
    st.session_state.flipped.append(idx)
    if len(st.session_state.flipped) == 2:
        st.session_state.moves += 1
        i, j = st.session_state.flipped
        ci, cj = st.session_state.cards[i], st.session_state.cards[j]

        # Vergelijk op naam (sprite-dict) of direct (emoji string)
        match = (
            ci["name"] == cj["name"]
            if isinstance(ci, dict) and isinstance(cj, dict)
            else ci == cj
        )

        if match:
            st.session_state.matched[i] = st.session_state.matched[j] = True
            st.session_state.matched_by[i] = st.session_state.matched_by[j] = st.session_state.current_player
            st.session_state.matches += 1
            if st.session_state.mode == "two":
                if st.session_state.current_player == 1: st.session_state.score_p1 += 1
                else: st.session_state.score_p2 += 1
            st.session_state.flipped = []
        else:
            st.session_state.lock = True

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 1 — Mode selection
# ─────────────────────────────────────────────────────────────────────────────
if "mode" not in st.session_state:
    st.markdown("# 🐷 Peppa's Memory Game")
    st.markdown('<p class="peppa-sub">Choose how you want to play! 🌟</p>', unsafe_allow_html=True)

    # Toon asset status
    if USE_SPRITES:
        names = ", ".join(s["label"] for s in SPRITES)
        st.markdown(f'<div class="asset-info">🖼️ {len(SPRITES)} sprite{"s" if len(SPRITES)>1 else ""} geladen: {names}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="asset-info">💡 Geen sprites gevonden in assets/ — emoji modus actief. Voeg PNG bestanden toe aan de assets/ map!</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="background:linear-gradient(135deg,#fce7f3,#fdf2f8);border:3px solid #e91e8c;border-radius:24px;padding:28px 16px;text-align:center;margin:6px"><div style="font-size:3rem">🐷</div><div style="font-size:1.3rem;font-weight:800;color:#be185d">Single Player</div><div style="color:#be185d;font-size:0.9rem">Play solo &amp; beat your score!</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Play Solo", use_container_width=True, key="btn_single"):
            st.session_state.mode = "single"; st.rerun()
    with col2:
        st.markdown('<div style="background:linear-gradient(135deg,#dbeafe,#eff6ff);border:3px solid #3b82f6;border-radius:24px;padding:28px 16px;text-align:center;margin:6px"><div style="font-size:3rem">🐷🐷</div><div style="font-size:1.3rem;font-weight:800;color:#1d4ed8">2 Players</div><div style="color:#1d4ed8;font-size:0.9rem">Take turns &amp; find more pairs!</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Play Together", use_container_width=True, key="btn_two"):
            st.session_state.mode = "two"; st.rerun()
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
            st.markdown(f'<div style="background:linear-gradient(135deg,{bg},{bg}99);border:3px solid {border};border-radius:24px;padding:24px 12px;text-align:center;margin:4px"><div style="font-size:3rem">{icon}</div><div style="font-size:1.2rem;font-weight:800;color:{fg};margin:6px 0">{diff}</div><div style="font-size:0.8rem;color:{fg};font-weight:700;margin-bottom:4px">{sublabel}</div><div style="color:{fg};font-size:0.85rem;opacity:0.85">{desc}</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"▶ {diff}", use_container_width=True, key=f"btn_diff_{diff}"):
                st.session_state.difficulty = diff; init_game(); st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back", use_container_width=True): go_home(); st.rerun()
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

# Kaartgrootte per moeilijkheid
SIZE_MAP = {"Easy": 90, "Medium": 72, "Hard": 58}
img_size = SIZE_MAP.get(diff, 72)

st.markdown("# 🐷 Peppa's Memory Game")
mode_label = "👤 Single Player" if st.session_state.mode == "single" else "👥 2 Players"
st.markdown(f'<p class="peppa-sub">{mode_label} &nbsp;·&nbsp;<span class="badge {badge_map[diff]}">{cfg["emoji"]} {diff}</span></p>', unsafe_allow_html=True)

if st.session_state.mode == "single":
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(f'<div class="score-box">🎯 Moves<br>{st.session_state.moves}</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="score-box">💖 Matches<br>{st.session_state.matches}/{n_pairs}</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="score-box">🃏 Left<br>{total-st.session_state.matches*2}</div>', unsafe_allow_html=True)
else:
    p1a = st.session_state.current_player == 1
    c1,cm,c2 = st.columns([2,1,2])
    with c1: st.markdown(f'<div class="{"score-p1" if p1a else "score-p1-off"}">🌸 Player 1{"◀TURN" if p1a else ""}<br>{st.session_state.score_p1} pairs</div>', unsafe_allow_html=True)
    with cm: st.markdown(f'<div class="score-box">🎯 {st.session_state.moves}</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="{"score-p2" if not p1a else "score-p2-off"}">🦋 Player 2{"◀TURN" if not p1a else ""}<br>{st.session_state.score_p2} pairs</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="turn-banner {"turn-p1" if p1a else "turn-p2"}">{"🌸 Player 1" if p1a else "🦋 Player 2"}\'s turn — flip two cards!</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Win / End check ───────────────────────────────────────────────────────────
if st.session_state.matches == n_pairs:
    if st.session_state.mode == "single":
        winner_label = "You"
        st.markdown(f'<div class="win-banner">🎉 Woohoo! You won! 🎉<br><span style="font-size:1rem;font-weight:400">All {n_pairs} pairs in <b>{st.session_state.moves}</b> moves on <b>{diff}</b>!</span><br>🐷🌈🌟🦋🍭🐸🎀🌸</div>', unsafe_allow_html=True)
    else:
        s1,s2 = st.session_state.score_p1, st.session_state.score_p2
        if s1>s2:   result,color,winner_label = f"🌸 Player 1 wins with {s1} pairs! 🎉","#be185d","Player 1"
        elif s2>s1: result,color,winner_label = f"🦋 Player 2 wins with {s2} pairs! 🎉","#1d4ed8","Player 2"
        else:       result,color,winner_label = f"🤝 It's a tie! {s1} pairs each!","#7c3aed","Both players"
        st.markdown(f'<div class="win-banner" style="border-color:{color};color:{color}">🎉 Game Over! 🎉<br><span style="font-size:1.1rem">{result}</span><br><span style="font-size:0.9rem;font-weight:400">🌸 P1:{s1} | 🦋 P2:{s2} · {diff}</span><br>🐷🌈🌟🦋🍭🐸🎀🌸</div>', unsafe_allow_html=True)

    st.balloons()
    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.get("score_saved", False):
        if not _can_save_score():
            st.warning(f"⚠️ You've saved {RATE_LIMIT} scores this session. Refresh the page to save more.")
        else:
            st.markdown(f'<div style="background:linear-gradient(135deg,#fef9c3,#fce7f3);border:2px solid #f59e0b;border-radius:20px;padding:16px;text-align:center;margin-bottom:12px"><div style="font-size:1.1rem;font-weight:800;color:#92400e">🏆 {winner_label} — enter your name for the Hall of Fame!</div></div>', unsafe_allow_html=True)
            name_input = st.text_input("", placeholder="Type your name here... 🌟", max_chars=_MAX_NAME_LEN, key="name_field", label_visibility="collapsed")
            if st.button("✅ Save my score!", use_container_width=True):
                clean_name = sanitize_name(name_input)
                save_score(
                    name=clean_name, difficulty=diff, mode=st.session_state.mode,
                    moves=st.session_state.moves, pairs=n_pairs,
                    date=datetime.now().strftime("%d %b %Y"),
                )
                _record_save()
                st.session_state.score_saved = True
                st.session_state.winner_name = clean_name
                st.rerun()
    else:
        saved_name = st.session_state.get("winner_name","")
        st.markdown(f'<div style="background:linear-gradient(135deg,#dcfce7,#d1fae5);border:2px solid #22c55e;border-radius:20px;padding:12px;text-align:center;margin-bottom:12px"><div style="font-size:1rem;font-weight:800;color:#15803d">✅ Score saved for <b>{saved_name}</b>! Great job! 🌟</div></div>', unsafe_allow_html=True)

    show_leaderboard(highlight_name=st.session_state.get("winner_name"))
    st.markdown("<br>", unsafe_allow_html=True)
    ca,cb,cc = st.columns(3)
    with ca:
        if st.button("🔄 Play Again", use_container_width=True): init_game(); st.rerun()
    with cb:
        if st.button("🎯 Change Difficulty", use_container_width=True):
            for k in ["difficulty","game_ready","score_saved"]: st.session_state.pop(k,None)
            st.rerun()
    with cc:
        if st.button("🏠 Main Menu", use_container_width=True): go_home(); st.rerun()
    st.stop()

# ── Grid ──────────────────────────────────────────────────────────────────────
grid_rows = [st.columns(cols) for _ in range(n_rows)]
for i in range(total):
    with grid_rows[i // cols][i % cols]:
        card = st.session_state.cards[i]

        if st.session_state.matched[i]:
            mcl  = "matched-p2" if st.session_state.matched_by[i] == 2 else "matched-p1"
            face = render_card_face(card, img_size)
            st.markdown(
                f'<div class="card-base {cclass} {mcl}">{face}</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.revealed[i]:
            face = render_card_face(card, img_size)
            st.markdown(
                f'<div class="card-base {cclass} flipped">{face}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button("🐷", key=f"card_{i}"):
                flip_card(i)
                st.rerun()

# ── Unmatched pair — flip back, switch player ─────────────────────────────────
if st.session_state.lock and len(st.session_state.flipped) == 2:
    time.sleep(0.9)
    i, j = st.session_state.flipped
    st.session_state.revealed[i] = st.session_state.revealed[j] = False
    st.session_state.flipped = []
    st.session_state.lock = False
    if st.session_state.mode == "two":
        st.session_state.current_player = 2 if st.session_state.current_player == 1 else 1
    st.rerun()

# ── Bottom nav ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
ca,cb,cc = st.columns(3)
with ca:
    if st.button("🔄 New Game", use_container_width=True): init_game(); st.rerun()
with cb:
    if st.button("🎯 Difficulty", use_container_width=True):
        for k in ["difficulty","game_ready"]: st.session_state.pop(k,None)
        st.rerun()
with cc:
    if st.button("🏠 Menu", use_container_width=True): go_home(); st.rerun()
