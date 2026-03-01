import streamlit as st
import random
import time

st.set_page_config(page_title="Peppa Pig Memory Game 🐷", page_icon="🐷", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Baloo 2', cursive; background-color: #fff0f5; }
h1 { font-size: 2.6rem !important; color: #e91e8c !important; text-align: center; }
div.stButton > button { width:90px; height:90px; font-size:2.2rem; border-radius:16px; border:3px solid #f9a8d4; background:linear-gradient(135deg,#ffd6ec,#fff0fa); box-shadow:0 4px 12px rgba(233,30,140,0.15); transition:transform 0.15s; padding:0; line-height:1; }
div.stButton > button:hover { transform:scale(1.08); border-color:#e91e8c; }
.matched-card { width:90px; height:90px; font-size:2.2rem; border-radius:16px; border:3px solid #86efac; background:linear-gradient(135deg,#d1fae5,#f0fdf4); display:flex; align-items:center; justify-content:center; }
.flipped-card { width:90px; height:90px; font-size:2.2rem; border-radius:16px; border:3px solid #e91e8c; background:linear-gradient(135deg,#fce7f3,#fdf2f8); display:flex; align-items:center; justify-content:center; }
.score-box { background:linear-gradient(135deg,#fce7f3,#fdf2f8); border:2px solid #f9a8d4; border-radius:20px; padding:12px 24px; text-align:center; margin:8px 4px; color:#be185d; font-weight:700; font-size:1.05rem; }
.win-banner { background:linear-gradient(135deg,#fce7f3,#bfdbfe); border:3px solid #e91e8c; border-radius:24px; padding:24px; text-align:center; font-size:1.5rem; color:#9d174d; font-weight:800; }
</style>""", unsafe_allow_html=True)

EMOJIS = ["🐷","🌈","🌟","🦋","🍭","🐸","🎀","🌸"]

def init_game():
    cards = EMOJIS * 2
    random.shuffle(cards)
    st.session_state.cards    = cards
    st.session_state.revealed = [False] * 16
    st.session_state.matched  = [False] * 16
    st.session_state.flipped  = []
    st.session_state.moves    = 0
    st.session_state.matches  = 0
    st.session_state.lock     = False

if "cards" not in st.session_state:
    init_game()

st.markdown("# 🐷 Peppa's Memory Game")

c1,c2,c3 = st.columns(3)
with c1: st.markdown(f'<div class="score-box">🎯 Moves<br>{st.session_state.moves}</div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="score-box">💖 Matches<br>{st.session_state.matches}/8</div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="score-box">🃏 Left<br>{16-st.session_state.matches*2}</div>', unsafe_allow_html=True)
st.markdown("---")

if st.session_state.matches == 8:
    st.markdown(f'<div class="win-banner">🎉 You won in {st.session_state.moves} moves! 🎉<br>🐷🌈🌟🦋🍭🐸🎀🌸</div>', unsafe_allow_html=True)
    st.balloons()
    if st.button("🔄 Play Again!"): init_game(); st.rerun()
    st.stop()

def flip_card(idx):
    if st.session_state.lock or st.session_state.matched[idx] or st.session_state.revealed[idx] or idx in st.session_state.flipped: return
    st.session_state.revealed[idx] = True
    st.session_state.flipped.append(idx)
    if len(st.session_state.flipped) == 2:
        st.session_state.moves += 1
        i,j = st.session_state.flipped
        if st.session_state.cards[i] == st.session_state.cards[j]:
            st.session_state.matched[i] = st.session_state.matched[j] = True
            st.session_state.matches += 1
            st.session_state.flipped = []
        else:
            st.session_state.lock = True

rows = [st.columns(4) for _ in range(4)]
for i in range(16):
    with rows[i//4][i%4]:
        if st.session_state.matched[i]: st.markdown(f'<div class="matched-card">{st.session_state.cards[i]}</div>', unsafe_allow_html=True)
        elif st.session_state.revealed[i]: st.markdown(f'<div class="flipped-card">{st.session_state.cards[i]}</div>', unsafe_allow_html=True)
        else:
            if st.button("🐷", key=f"card_{i}"): flip_card(i); st.rerun()

if st.session_state.lock and len(st.session_state.flipped)==2:
    time.sleep(0.9)
    i,j = st.session_state.flipped
    st.session_state.revealed[i] = st.session_state.revealed[j] = False
    st.session_state.flipped = []; st.session_state.lock = False; st.rerun()

if st.button("🔄 New Game", use_container_width=True): init_game(); st.rerun()
