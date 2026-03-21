import streamlit as st

st.set_page_config(
    page_title="Peppa's Speelplein 🐷",
    page_icon="🐷",
    layout="centered",
)

# st.html() werkt correct in Streamlit 1.44+
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none; }
div[data-testid="stDecoration"] { display: none; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #87CEEB 0%, #B0E0FF 55%, #C8EFA0 80%, #7EC850 100%) !important;
    min-height: 100vh;
}
[data-testid="stMain"], .main, .main > div {
    background: transparent !important;
}

.clouds-wrap {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 160px;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.cloud {
    position: absolute;
    background: white;
    border-radius: 50px;
    opacity: 0.85;
}
.cloud::before, .cloud::after {
    content: '';
    position: absolute;
    background: white;
    border-radius: 50%;
}
.c1 { width:90px; height:34px; top:30px; animation: fc 18s linear infinite; }
.c1::before { width:44px; height:44px; top:-22px; left:12px; }
.c1::after  { width:30px; height:30px; top:-15px; left:40px; }
.c2 { width:120px; height:44px; top:70px; animation: fc 24s linear infinite 6s; }
.c2::before { width:58px; height:58px; top:-29px; left:18px; }
.c2::after  { width:44px; height:44px; top:-22px; left:55px; }
.c3 { width:70px; height:26px; top:15px; animation: fc 20s linear infinite 12s; }
.c3::before { width:34px; height:34px; top:-17px; left:10px; }
.c3::after  { width:24px; height:24px; top:-12px; left:32px; }
@keyframes fc {
    from { transform: translateX(-200px); }
    to   { transform: translateX(calc(100vw + 200px)); }
}

.sun {
    position: fixed;
    top: 20px; right: 60px;
    width: 70px; height: 70px;
    background: radial-gradient(circle, #FFE566, #FFD93D);
    border-radius: 50%;
    box-shadow: 0 0 0 12px rgba(255,217,61,0.2), 0 0 0 24px rgba(255,217,61,0.1);
    animation: sunPulse 3s ease-in-out infinite;
    z-index: 0;
    pointer-events: none;
}
@keyframes sunPulse {
    0%,100% { box-shadow: 0 0 0 12px rgba(255,217,61,0.2), 0 0 0 24px rgba(255,217,61,0.1); }
    50%      { box-shadow: 0 0 0 18px rgba(255,217,61,0.28), 0 0 0 36px rgba(255,217,61,0.13); }
}

.grass {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    height: 60px;
    background: linear-gradient(to bottom, #7EC850, #6AA63E);
    border-radius: 50% 50% 0 0 / 18px 18px 0 0;
    pointer-events: none;
    z-index: 0;
}

.hub-content {
    position: relative;
    z-index: 1;
    padding: 16px 12px 80px 12px;
}

.hub-title {
    font-family: 'Fredoka One', cursive;
    font-size: clamp(2rem, 7vw, 3.4rem);
    color: #C2185B;
    text-align: center;
    text-shadow: 2px 2px 0 white, 4px 4px 0 rgba(255,255,255,0.4);
    line-height: 1.1;
    margin-bottom: 4px;
}
.hub-sub {
    font-family: 'Fredoka One', cursive;
    font-size: clamp(0.9rem, 3vw, 1.2rem);
    color: #FFD93D;
    text-align: center;
    text-shadow: 1px 1px 0 rgba(0,0,0,0.2);
    margin-bottom: 16px;
}

.game-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    max-width: 800px;
    margin: 0 auto;
}
@media (max-width: 640px) {
    .game-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
}
@media (min-width: 641px) and (max-width: 900px) {
    .game-grid { grid-template-columns: repeat(3, 1fr); }
}

.tile {
    background: #FFFEF7;
    border-radius: 20px;
    padding: 16px 10px 12px;
    text-align: center;
    cursor: pointer;
    border: 4px solid transparent;
    box-shadow: 0 5px 0 rgba(0,0,0,0.1), 0 8px 20px rgba(0,0,0,0.08);
    transition: transform 0.18s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.18s;
    position: relative;
    overflow: hidden;
    text-decoration: none;
    display: block;
}
.tile:hover {
    transform: translateY(-5px) scale(1.03);
    box-shadow: 0 10px 0 rgba(0,0,0,0.1), 0 16px 30px rgba(0,0,0,0.13);
}

.tile-1 { border-color: #FF6B9D; }
.tile-2 { border-color: #FF8C42; }
.tile-3 { border-color: #6BCB77; }
.tile-4 { border-color: #4D9DE0; }
.tile-5 { border-color: #9B5DE5; }
.tile-6 { border-color: #00C9A7; }
.tile-7 { border-color: #FF4757; }
.tile-8 { border-color: #FFC107; }

.tile-icon {
    font-size: clamp(2rem, 5vw, 2.6rem);
    display: block;
    margin-bottom: 6px;
    transition: transform 0.2s;
}
.tile:hover .tile-icon { transform: scale(1.2) rotate(-5deg); }

.tile-num {
    position: absolute;
    top: 6px; right: 8px;
    font-family: 'Fredoka One', cursive;
    font-size: 0.7rem;
    color: #ccc;
}

.tile-name {
    font-family: 'Fredoka One', cursive;
    font-size: clamp(0.8rem, 2.5vw, 1rem);
    color: #333;
    line-height: 1.2;
    margin-bottom: 4px;
}

.tile-desc {
    font-size: clamp(0.55rem, 1.5vw, 0.65rem);
    color: #999;
    font-weight: 700;
    line-height: 1.3;
}

.chip-ready {
    position: absolute;
    top: 6px; left: 6px;
    background: #6BCB77;
    color: white;
    font-family: 'Fredoka One', cursive;
    font-size: 0.5rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 20px;
}
.chip-soon {
    position: absolute;
    top: 6px; left: 6px;
    background: #ddd;
    color: white;
    font-family: 'Fredoka One', cursive;
    font-size: 0.5rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 20px;
}

.sticker-bar {
    max-width: 800px;
    margin: 16px auto 0;
    background: rgba(255,255,255,0.88);
    border-radius: 16px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    box-shadow: 0 4px 15px rgba(0,0,0,0.07);
}
.sticker-label {
    font-family: 'Fredoka One', cursive;
    color: #E0447A;
    font-size: 0.9rem;
    white-space: nowrap;
}
.sticker-slot {
    width: 34px; height: 34px;
    border-radius: 8px;
    border: 3px dashed #FFB3CC;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    background: rgba(255,179,204,0.08);
}
.sticker-slot.filled {
    border-style: solid;
    border-color: #FF6B9D;
    background: rgba(255,107,157,0.06);
}
</style>

<div class="sun"></div>
<div class="clouds-wrap">
    <div class="cloud c1"></div>
    <div class="cloud c2"></div>
    <div class="cloud c3"></div>
</div>
<div class="grass"></div>

<div class="hub-content">
    <div class="hub-title">🐷 Peppa's Speelplein</div>
    <div class="hub-sub">Kies een spel en begin met spelen!</div>

    <div class="game-grid">

        <a class="tile tile-1" href="/Verschillen" target="_self">
            <div class="chip-soon">Binnenkort</div>
            <span class="tile-num">1</span>
            <span class="tile-icon">🔍</span>
            <div class="tile-name">Zoek de Verschillen</div>
            <div class="tile-desc">2 plaatjes · 4 verschillen</div>
        </a>

        <a class="tile tile-2" href="/memory" target="_self">
            <div class="chip-ready">✓ Klaar!</div>
            <span class="tile-num">2</span>
            <span class="tile-icon">🃏</span>
            <div class="tile-name">Memory Spel</div>
            <div class="tile-desc">Vind alle kaartparen</div>
        </a>

        <a class="tile tile-3" href="/Stickers" target="_self">
            <div class="chip-soon">Binnenkort</div>
            <span class="tile-num">3</span>
            <span class="tile-icon">⭐</span>
            <div class="tile-name">Sticker Puzzel</div>
            <div class="tile-desc">Zoek het juiste karakter</div>
        </a>

        <a class="tile tile-4" href="/Nummers" target="_self">
            <div class="chip-soon">Binnenkort</div>
            <span class="tile-num">4</span>
            <span class="tile-icon">🔢</span>
            <div class="tile-name">Verbind 1 t/m 20</div>
            <div class="tile-desc">Trek lijntjes · Onthul sticker</div>
        </a>

        <a class="tile tile-5" href="/Kledingkast" target="_self">
            <div class="chip-soon">Binnenkort</div>
            <span class="tile-num">5</span>
            <span class="tile-icon">👗</span>
            <div class="tile-name">Kledingkast</div>
            <div class="tile-desc">Kleed Peppa aan!</div>
        </a>

        <a class="tile tile-6" href="/Puzzel" target="_self">
            <div class="chip-soon">Binnenkort</div>
            <span class="tile-num">6</span>
            <span class="tile-icon">🧩</span>
            <div class="tile-name">Legpuzzel</div>
            <div class="tile-desc">3×3 raster · Sleep stukjes</div>
        </a>

        <a class="tile tile-7" href="/Voertuig" target="_self">
            <div class="chip-soon">Binnenkort</div>
            <span class="tile-num">7</span>
            <span class="tile-icon">🚛</span>
            <div class="tile-name">Bouw een Voertuig</div>
            <div class="tile-desc">Wielen · Lading · Cabine</div>
        </a>

        <a class="tile tile-8" href="/Topografie" target="_self">
            <div class="chip-soon">Binnenkort</div>
            <span class="tile-num">8</span>
            <span class="tile-icon">🗺️</span>
            <div class="tile-name">Topografie NL</div>
            <div class="tile-desc">12 provincies · Sleep!</div>
        </a>

    </div>

    <div class="sticker-bar">
        <div class="sticker-label">🌟 Stickers:</div>
        <div class="sticker-slot filled">🐷</div>
        <div class="sticker-slot">?</div>
        <div class="sticker-slot">?</div>
        <div class="sticker-slot">?</div>
        <div class="sticker-slot">?</div>
        <div class="sticker-slot">?</div>
        <div class="sticker-slot">?</div>
        <div class="sticker-slot">?</div>
    </div>
</div>
""")
