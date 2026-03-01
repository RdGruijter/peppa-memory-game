import streamlit as st
import random
import time

st.set_page_config(page_title="Peppa Pig Memory Game 🐷", page_icon="🐷", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Baloo 2', cursive; background-color: #fff0f5; }
h1 { font-size: 2.6rem !important; color: #e91e8c !important; text-align: center; }
div.stButton > button { font-family:'Baloo 2',cursive; border-radius:16px; border:3px solid #f9a8d4; background:linear-gradient(135deg,#ffd6ec,#fff0fa); box-shadow:0 4px 12px rgba(233,30,140,0.15); transition:transform 0.15s; cursor:pointer; font-weight:700; }
div.stButton > button:hover { transform:scale(1.05); border-color:#e91e8c; }
.card-medium { width:90px; height:90px; font-size:2.2rem; }
.card-base { border-radius:16px; display:flex; align-items:center; justify-content:center; }
.matched-p1 { border:3px solid #86efac; background:linear-gradient(135deg,#d1fae5,#f0fdf4); }
.matched-p2 { border:3px solid #93c5fd; background:linear-gradient(135deg,#dbeafe,#eff6ff); }
.flipped    { border:3px solid #e91e8c; background:linear-gradient(135deg,#fce7f3,#fdf2f8); }
.score-box    { background:linear-gradient(135deg,#fce7f3,#fdf2f8); border:2px solid #f9a8d4; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; color:#be185d; font-weight:700; font-size:1rem; }
.score-p1     { border:3px solid #e91e8c; background:linear-gradient(135deg,#fce7f3,#fdf2f8); color:#be185d; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; font-weight:700; font-size:1rem; }
.score-p1-off { border:2px dashed #f9a8d4; background:#fdf2f8; color:#f9a8d4; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; font-weight:700; font-size:1rem; }
.score-p2     { border:3px solid #3b82f6; background:linear-gradient(135deg,#dbeafe,#eff6ff); color:#1d4ed8; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; font-weight:700; font-size:1rem; }
.score-p2-off { border:2px dashed #93c5fd; background:#eff6ff; color:#93c5fd; border-radius:20px; padding:10px 16px; text-align:center; margin:6px 2px; font-weight:700; font-size:1rem; }
.turn-banner { border-radius:16px; padding:8px 20px; text-align:center; font-size:1.15rem; font-weight:800; margin:6px 0 10px 0; }
.turn-p1 { background:linear-gradient(135deg,#fce7f3,#fdf2f8); border:2px solid #e91e8c; color:#be185d; }
.turn-p2 { background:linear-gradient(135deg,#dbeafe,#eff6ff); border:2px solid #3b82f6; color:#1d4ed8; }
.win-banner { background:linear-gradient(135deg,#fce7f3,#bfdbfe); border:3px solid #e91e8c; border-radius:24px; padding:24px; text-align:center; font-size:1.5rem; color:#9d174d; font-weight:800; }
.peppa-sub { text-align:center; font-size:1rem; color:#be185d; margin-bottom:4px; }
</style>""", unsafe_allow_html=True)

EMOJIS = ["🐷","🌈","🌟","🦋","🍭","🐸","🎀","🌸"]

def init_game(mode="single"):
    cards = EMOJIS * 2; random.shuffle(cards)
    st.session_state.update(dict(cards=cards, revealed=[False]*16, matched=[False]*16,
        matched_by=[None]*16, flipped=[], moves=0, matches=0, lock=False,
        mode=mode, current_player=1, score_p1=0, score_p2=0))

def go_home():
    st.session_state.pop("mode", None)

if "mode" not in st.session_state:
    st.markdown("# 🐷 Peppa's Memory Game")
    st.markdown('<p class="peppa-sub">Choose how you want to play! 🌟</p>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div style="background:linear-gradient(135deg,#fce7f3,#fdf2f8);border:3px solid #e91e8c;border-radius:24px;padding:28px 16px;text-align:center;margin:6px"><div style="font-size:3rem">🐷</div><div style="font-size:1.3rem;font-weight:800;color:#be185d">Single Player</div><div style="color:#be185d;font-size:0.9rem">Play solo &amp; beat your score!</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Play Solo", use_container_width=True): init_game("single"); st.rerun()
    with c2:
        st.markdown('<div style="background:linear-gradient(135deg,#dbeafe,#eff6ff);border:3px solid #3b82f6;border-radius:24px;padding:28px 16px;text-align:center;margin:6px"><div style="font-size:3rem">🐷🐷</div><div style="font-size:1.3rem;font-weight:800;color:#1d4ed8">2 Players</div><div style="color:#1d4ed8;font-size:0.9rem">Take turns &amp; find more pairs!</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Play Together", use_container_width=True): init_game("two"); st.rerun()
    st.stop()

st.markdown("# 🐷 Peppa's Memory Game")
mode_label = "👤 Single Player" if st.session_state.mode=="single" else "👥 2 Players"
st.markdown(f'<p class="peppa-sub">{mode_label}</p>', unsafe_allow_html=True)

if st.session_state.mode=="single":
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(f'<div class="score-box">🎯 Moves<br>{st.session_state.moves}</div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="score-box">💖 Matches<br>{st.session_state.matches}/8</div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="score-box">🃏 Left<br>{16-st.session_state.matches*2}</div>',unsafe_allow_html=True)
else:
    p1a=st.session_state.current_player==1
    c1,cm,c2=st.columns([2,1,2])
    with c1: st.markdown(f'<div class="{"score-p1" if p1a else "score-p1-off"}">🌸 Player 1{"◀TURN" if p1a else ""}<br>{st.session_state.score_p1} pairs</div>',unsafe_allow_html=True)
    with cm: st.markdown(f'<div class="score-box">🎯{st.session_state.moves}</div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="{"score-p2" if not p1a else "score-p2-off"}">🦋 Player 2{"◀TURN" if not p1a else ""}<br>{st.session_state.score_p2} pairs</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="turn-banner {"turn-p1" if p1a else "turn-p2"}">{"🌸 Player 1" if p1a else "🦋 Player 2"}\'s turn!</div>',unsafe_allow_html=True)
st.markdown("---")

if st.session_state.matches==8:
    if st.session_state.mode=="single":
        st.markdown(f'<div class="win-banner">🎉 You won in {st.session_state.moves} moves! 🎉</div>',unsafe_allow_html=True)
    else:
        s1,s2=st.session_state.score_p1,st.session_state.score_p2
        r,col=(f"🌸 P1 wins! {s1} pairs","#be185d") if s1>s2 else ((f"🦋 P2 wins! {s2} pairs","#1d4ed8") if s2>s1 else ("🤝 Tie!","#7c3aed"))
        st.markdown(f'<div class="win-banner" style="color:{col};border-color:{col}">🎉 {r} 🎉</div>',unsafe_allow_html=True)
    st.balloons()
    ca,cb=st.columns(2)
    with ca:
        if st.button("🔄 Play Again",use_container_width=True): init_game(st.session_state.mode); st.rerun()
    with cb:
        if st.button("🏠 Menu",use_container_width=True): go_home(); st.rerun()
    st.stop()

def flip_card(idx):
    if st.session_state.lock or st.session_state.matched[idx] or st.session_state.revealed[idx] or idx in st.session_state.flipped: return
    st.session_state.revealed[idx]=True; st.session_state.flipped.append(idx)
    if len(st.session_state.flipped)==2:
        st.session_state.moves+=1; i,j=st.session_state.flipped
        if st.session_state.cards[i]==st.session_state.cards[j]:
            st.session_state.matched[i]=st.session_state.matched[j]=True
            st.session_state.matched_by[i]=st.session_state.matched_by[j]=st.session_state.current_player
            st.session_state.matches+=1
            if st.session_state.mode=="two":
                if st.session_state.current_player==1: st.session_state.score_p1+=1
                else: st.session_state.score_p2+=1
            st.session_state.flipped=[]
        else: st.session_state.lock=True

rows=[st.columns(4) for _ in range(4)]
for i in range(16):
    with rows[i//4][i%4]:
        if st.session_state.matched[i]:
            mcl="matched-p2" if st.session_state.matched_by[i]==2 else "matched-p1"
            st.markdown(f'<div class="card-base card-medium {mcl}">{st.session_state.cards[i]}</div>',unsafe_allow_html=True)
        elif st.session_state.revealed[i]: st.markdown(f'<div class="card-base card-medium flipped">{st.session_state.cards[i]}</div>',unsafe_allow_html=True)
        else:
            if st.button("🐷",key=f"card_{i}"): flip_card(i); st.rerun()

if st.session_state.lock and len(st.session_state.flipped)==2:
    time.sleep(0.9); i,j=st.session_state.flipped
    st.session_state.revealed[i]=st.session_state.revealed[j]=False
    st.session_state.flipped=[]; st.session_state.lock=False
    if st.session_state.mode=="two": st.session_state.current_player=2 if st.session_state.current_player==1 else 1
    st.rerun()

ca,cb=st.columns(2)
with ca:
    if st.button("🔄 New Game",use_container_width=True): init_game(st.session_state.mode); st.rerun()
with cb:
    if st.button("🏠 Menu",use_container_width=True): go_home(); st.rerun()
