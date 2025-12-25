import streamlit as st
import os
import random

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="SonicStream Player",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- Initialize Session State ----------------
if 'current_song_index' not in st.session_state:
    st.session_state.current_song_index = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'volume' not in st.session_state:
    st.session_state.volume = 0.7
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'shuffle' not in st.session_state:
    st.session_state.shuffle = False
if 'repeat' not in st.session_state:
    st.session_state.repeat = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'user_interacted' not in st.session_state:
    st.session_state.user_interacted = False

# ---------------- CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Poppins', sans-serif; }
    
    body {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        min-height: 100vh;
        color: white;
        margin: 0;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* --- START SCREEN --- */
    .start-screen-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 60vh; text-align: center;
    }
    .start-title {
        font-size: 52px; font-weight: 800;
        background: linear-gradient(to right, #fff, #00d2ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        margin-bottom: 10px; letter-spacing: 2px;
    }
    
    /* --- NEW STYLE: FUTURISTIC GLASS BUTTON --- */
    button[data-testid="baseButton-primary"] {
        /* Glass Effect */
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        
        /* Border */
        border: 1px solid rgba(255, 255, 255, 0.2);
        
        /* Shape & Layout */
        border-radius: 8px; /* More square/techy than round */
        width: 100%;
        padding: 18px;
        
        /* Typography */
        color: rgba(255, 255, 255, 0.9);
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        font-size: 16px;
        
        /* Shadow & Transition */
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
    }

    /* Hover Effect */
    button[data-testid="baseButton-primary"]:hover {
        background: rgba(0, 210, 255, 0.15);
        border-color: #00d2ff;
        box-shadow: 0 0 25px rgba(0, 210, 255, 0.5), inset 0 0 10px rgba(0, 210, 255, 0.2);
        letter-spacing: 5px; /* Letters spread out */
        transform: translateY(-3px);
    }

    /* Click Effect */
    button[data-testid="baseButton-primary"]:active {
        transform: scale(0.98);
    }

    /* --- MODE SELECTOR (PILL SHAPE) --- */
    div[data-testid="stRadio"] {
        display: flex; justify-content: center; margin-bottom: 30px;
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex; background-color: rgba(255, 255, 255, 0.1);
        border-radius: 50px; padding: 5px; gap: 5px;
        width: 100%; max-width: 400px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex: 1; display: flex; justify-content: center; align-items: center;
        border-radius: 40px; cursor: pointer; transition: all 0.3s ease;
        margin: 0; height: 50px;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label > input { display: none; }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div {
        color: rgba(255, 255, 255, 0.6); font-size: 16px; font-weight: 500;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label > input:checked + div {
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        color: white; border-radius: 40px; width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 2px 10px rgba(0, 210, 255, 0.3);
    }

    /* --- PLAYER UI --- */
    .glass-card {
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(16px);
        border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 30px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); margin-bottom: 25px;
    }
    
    .album-art-container {
        position: relative; width: 220px; height: 220px; margin: 0 auto 25px;
        display: flex; align-items: center; justify-content: center;
    }
    .album-art {
        width: 100%; height: 100%; border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex; align-items: center; justify-content: center; font-size: 90px;
        position: relative; z-index: 2; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        animation: rotate 20s linear infinite;
    }
    .album-art.paused { animation-play-state: paused; }
    .album-glow {
        position: absolute; top: -10%; left: -10%; width: 120%; height: 120%;
        border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        z-index: 1; filter: blur(20px); opacity: 0.6; animation: pulseGlow 3s ease-in-out infinite;
    }
    @keyframes pulseGlow { 0% { transform: scale(0.95); opacity: 0.5; } 50% { transform: scale(1.05); opacity: 0.7; } 100% { transform: scale(0.95); opacity: 0.5; } }
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .visualizer-container {
        height: 70px; display: flex; align-items: flex-end; justify-content: center;
        gap: 4px; margin: 25px 0; padding: 20px; background: rgba(0, 0, 0, 0.15); border-radius: 20px;
    }
    .visualizer-bar {
        width: 6px; background: linear-gradient(to top, #00d2ff, #3a7bd5);
        border-radius: 4px; animation: bounce 1s ease-in-out infinite;
    }
    .visualizer-container.paused .visualizer-bar { animation-play-state: paused; height: 10px !important; opacity: 0.3; }
    @keyframes bounce { 0%, 100% { height: 10px; } 50% { height: var(--bar-height); } }

    .stButton > button {
        border: none; background: rgba(255,255,255,0.1); color: white;
        transition: all 0.2s ease; border-radius: 50%; width: 50px; height: 50px;
        font-size: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .stButton > button:hover { background: rgba(255,255,255,0.2); transform: translateY(-2px); }
    
    div:has(> button[key="play"]) > button {
        width: 70px; height: 70px; font-size: 28px;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        box-shadow: 0 8px 25px rgba(0, 210, 255, 0.4);
    }

    .stAudio { display: none; }

    .playlist-item {
        padding: 15px; margin: 8px 0; background: rgba(255, 255, 255, 0.05);
        border-radius: 12px; transition: all 0.3s ease; border: 1px solid transparent;
    }
    .playlist-item:hover { background: rgba(255, 255, 255, 0.1); }
    .playlist-item.active {
        background: rgba(0, 210, 255, 0.15); border: 1px solid rgba(0, 210, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- START SCREEN (NEW STYLE) ----------------
if not st.session_state.user_interacted:
    c1, c2, c3 = st.columns([1, 2, 1])

    with c2:
        st.markdown("""
        <div class="start-screen-container">
            <div class="start-title">SONICSTREAM</div>
            <p style="opacity: 0.6; margin-bottom: 50px; font-size: 14px; letter-spacing: 1px;">AUDIO ENGINE READY</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Changed text to "INITIALIZE SYSTEM"
        if st.button("▶ INITIALIZE SYSTEM", key="start_btn", type="primary"):
            st.session_state.user_interacted = True
            st.rerun()
    
    st.stop()

# ---------------- HEADER ----------------
st.markdown("""
<div class="glass-card" style="text-align: center; padding: 15px;">
    <h1 style="margin: 0; font-size: 28px; background: -webkit-linear-gradient(#00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SonicStream</h1>
</div>
""", unsafe_allow_html=True)

# ---------------- MODE SELECTOR ----------------
mode = st.radio(
    "",
    ["📤 Upload", "📁 Folder"],
    horizontal=True,
    label_visibility="collapsed"
)

# ---------------- LOAD LOGIC ----------------
if mode == "📤 Upload":
    st.markdown("""
    <div style="text-align: center; padding: 30px; border: 2px dashed rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 20px;">
        <span style="font-size: 40px;">📂</span>
        <p style="margin: 10px 0 0 0; opacity: 0.7;">Drag & Drop Files Here</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("", type=["wav", "mp3", "ogg"], accept_multiple_files=True, label_visibility="collapsed")

    if uploaded_files:
        st.session_state.playlist = []
        for f in uploaded_files:
            st.session_state.playlist.append({
                "name": f.name,
                "bytes": f.read(),
                "format": f.type
            })
else:
    music_folder = "music"
    if not os.path.isdir(music_folder):
        st.warning("Folder 'music' not found.")
    else:
        files = [f for f in os.listdir(music_folder) if f.lower().endswith((".wav", ".mp3"))]
        if files:
            st.session_state.playlist = []
            for f in files:
                path = os.path.join(music_folder, f)
                with open(path, "rb") as audio:
                    st.session_state.playlist.append({
                        "name": f,
                        "bytes": audio.read(),
                        "format": f"audio/{f.split('.')[-1].lower()}"
                    })

# ---------------- PLAYER UI ----------------
if st.session_state.playlist:
    current_song = st.session_state.playlist[st.session_state.current_song_index]
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Album Art
    art_state = "" if st.session_state.is_playing else "paused"
    st.markdown(f"""
    <div class="album-art-container">
        <div class="album-glow"></div>
        <div class="album-art {art_state}">🎵</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Song Info
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="font-size: 22px; margin: 0; word-break: break-all;">{current_song['name']}</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 14px;">
            {'Now Playing' if st.session_state.is_playing else 'Paused'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualizer
    vis_state = "" if st.session_state.is_playing else "paused"
    bars = "".join([
        f'<div class="visualizer-bar" style="--bar-height: {random.randint(15, 60)}px; animation-duration: {random.uniform(0.8, 1.2)}s; animation-delay: {random.uniform(0, 0.5)}s"></div>' 
        for i in range(25)
    ])
    st.markdown(f"""
    <div class="visualizer-container {vis_state}">
        {bars}
    </div>
    """, unsafe_allow_html=True)
    
    # Controls
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1.5, 1, 1])
    
    with c1:
        if st.button("⏮", key="prev"):
            st.session_state.current_song_index = (st.session_state.current_song_index - 1) % len(st.session_state.playlist)
            st.session_state.is_playing = True
            st.rerun()
    with c2:
        if st.button("🔀", key="shuffle"):
            st.session_state.shuffle = not st.session_state.shuffle
            st.rerun()
    with c3:
        play_icon = "⏸" if st.session_state.is_playing else "▶"
        if st.button(play_icon, key="play", use_container_width=True):
            st.session_state.is_playing = not st.session_state.is_playing
            st.rerun()
    with c4:
        if st.button("🔁", key="repeat"):
            st.session_state.repeat = not st.session_state.repeat
            st.rerun()
    with c5:
        if st.button("⏭", key="next"):
            st.session_state.current_song_index = (st.session_state.current_song_index + 1) % len(st.session_state.playlist)
            st.session_state.is_playing = True
            st.rerun()
            
    # Volume
    vol = st.slider("Volume", 0.0, 1.0, st.session_state.volume, label_visibility="collapsed")
    st.session_state.volume = vol
    
    # Audio Logic
    if st.session_state.is_playing:
        st.audio(current_song["bytes"], format=current_song["format"], start_time=st.session_state.start_time, autoplay=True)
    else:
        st.audio(current_song["bytes"], format=current_song["format"], start_time=st.session_state.start_time, autoplay=False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Playlist
    st.markdown('<div class="glass-card playlist-section">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0;">📋 Playlist</h3>', unsafe_allow_html=True)
    
    for i, song in enumerate(st.session_state.playlist):
        active = "active" if i == st.session_state.current_song_index else ""
        icon = "▶" if active else "🎵"
        col_song, col_btn = st.columns([5, 1])
        with col_song:
            st.markdown(f'<div class="playlist-item {active}">{icon} {song["name"]}</div>', unsafe_allow_html=True)
        with col_btn:
            if st.button("▶", key=f"play_{i}"):
                st.session_state.current_song_index = i
                st.session_state.is_playing = True
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 50px;">
        <h2 style="opacity: 0.5;">No Music Loaded</h2>
        <p style="opacity: 0.3;">Please upload files or select a folder.</p>
    </div>
    """, unsafe_allow_html=True)
