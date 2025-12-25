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
# NEW: User selected accent color (Default is Neon Blue)
if 'accent_color' not in st.session_state:
    st.session_state.accent_color = "#00d2ff"

# ---------------- DYNAMIC CSS ----------------
# We inject the user's color choice into CSS variables
accent = st.session_state.accent_color

st.markdown(f"""
<style>
    :root {{
        --primary-color: {accent};
        --primary-dim: {accent}33; /* 20% opacity */
    }}

    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Rajdhani:wght@500;700&display=swap');
    
    * {{ font-family: 'Montserrat', sans-serif; }}
    
    /* --- BACKGROUND ANIMATIONS (PURE DARK THEME) --- */
    body {{
        /* Pure Black Background */
        background: #000000; 
        min-height: 100vh;
        color: white;
        margin: 0;
        overflow-x: hidden;
    }}
    
    /* Dark Subtle Gradient Background Layer */
    .bg-gradient {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        /* Very subtle dark grey to black radial */
        background: radial-gradient(circle at 50% 50%, #111111 0%, #000000 80%);
        z-index: -3;
    }}

    /* Floating Orbs - Dark & Subtle */
    .blob {{
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
        z-index: -2;
        opacity: 0.15; /* Reduced opacity for darker feel */
        animation: floatBlob 25s infinite ease-in-out alternate;
    }}
    
    .blob-1 {{
        width: 600px; height: 600px;
        background: radial-gradient(circle, var(--primary-color), transparent);
        top: -150px; left: -150px;
        animation-duration: 30s;
    }}
    
    .blob-2 {{
        width: 500px; height: 500px;
        background: radial-gradient(circle, #222, transparent); /* Dark grey secondary blob */
        bottom: -100px; right: -100px;
        animation-duration: 35s;
        animation-delay: -5s;
    }}

    @keyframes floatBlob {{
        0% {{ transform: translate(0, 0) scale(1); }}
        100% {{ transform: translate(50px, 50px) scale(1.1); }}
    }}

    /* --- START SCREEN --- */
    .start-screen-container {{
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 70vh; text-align: center;
    }}
    .start-title {{
        font-family: 'Rajdhani', sans-serif;
        font-size: 72px; font-weight: 700;
        background: linear-gradient(to right, var(--primary-color), #ffffff, var(--primary-color));
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        animation: shineText 5s linear infinite; margin-bottom: 0;
    }}

    @keyframes shineText {{ to {{ background-position: 200% center; }} }}
    
    button[data-testid="baseButton-primary"] {{
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid var(--primary-color);
        border-radius: 4px;
        width: 100%;
        padding: 20px;
        color: var(--primary-color);
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        font-size: 18px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 1);
        transition: all 0.3s ease;
    }}

    button[data-testid="baseButton-primary"]:hover {{
        background: var(--primary-dim);
        box-shadow: 0 0 40px var(--primary-color);
        transform: scale(1.02);
    }}

    /* --- GLASS CARDS (DARK THEME) --- */
    .glass-card {{
        /* Opaque dark background */
        background: rgba(0, 0, 0, 0.75); 
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08); /* Very subtle border */
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 1);
        margin-bottom: 30px;
    }}
    
    /* --- CONTROLS DECK --- */
    .controls-deck {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 25px;
        margin: 30px 0;
        position: relative;
    }}

    .stButton > button {{
        background: rgba(30, 30, 30, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.8);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 24px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.8);
    }}
    
    .stButton > button:hover {{
        background: rgba(40, 40, 40, 1);
        color: white;
        transform: translateY(-5px);
        box-shadow: 0 0 20px var(--primary-color);
        border-color: var(--primary-color);
    }}

    /* THE BIG PLAY BUTTON */
    div:has(> button[key="btn_play"]) > button {{
        width: 90px; height: 90px;
        font-size: 32px;
        background: linear-gradient(135deg, var(--primary-color), #111);
        border: none;
        color: white;
        position: relative;
        z-index: 2;
        
        box-shadow: 
            0 0 0 6px rgba(255, 255, 255, 0.05),
            0 0 30px var(--primary-color);
        animation: pulsePlay 2s infinite ease-in-out;
    }}

    div:has(> button[key="btn_play"]) > button:hover {{
        transform: scale(1.1);
        box-shadow: 
            0 0 0 10px rgba(255, 255, 255, 0.1),
            0 0 50px var(--primary-color);
    }}

    @keyframes pulsePlay {{
        0% {{ box-shadow: 0 0 0 0 var(--primary-color); }}
        70% {{ box-shadow: 0 0 0 20px rgba(0,0,0,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }}
    }}

    /* --- SONG INFO --- */
    .song-title {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 28px;
        background: -webkit-linear-gradient(#fff, #aaa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }}

    /* --- VISUALIZER --- */
    .visualizer-container {{
        height: 80px; display: flex; align-items: flex-end; justify-content: center;
        gap: 5px; margin: 30px 0; padding: 20px; background: rgba(20, 20, 20, 0.6); 
        border-radius: 15px; border: 1px solid rgba(255,255,255,0.05);
    }}
    .visualizer-bar {{
        width: 6px; background: linear-gradient(to top, var(--primary-color), #ffffff);
        border-radius: 3px; animation: bounce 1s ease-in-out infinite;
        box-shadow: 0 0 10px var(--primary-color);
    }}
    .visualizer-container.paused .visualizer-bar {{ animation-play-state: paused; height: 5px !important; opacity: 0.3; }}
    @keyframes bounce {{ 0%, 100% {{ height: 10px; }} 50% {{ height: var(--bar-height); }} }}

    /* --- MODE SELECTOR --- */
    div[data-testid="stRadio"] {{ display: flex; justify-content: center; margin-bottom: 30px; }}
    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex; background: rgba(20, 20, 20, 0.8); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 5px; gap: 5px; width: 100%; max-width: 400px;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {{
        flex: 1; border-radius: 8px; cursor: pointer; margin: 0; height: 45px;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > input {{ display: none; }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div {{
        color: rgba(255,255,255,0.5); font-weight: 600; font-size: 14px;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > input:checked + div {{
        background: linear-gradient(135deg, var(--primary-color), #000);
        color: white; box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }}

    /* --- PLAYLIST --- */
    .playlist-item {{
        padding: 15px; margin: 10px 0; background: rgba(255, 255, 255, 0.02);
        border-radius: 12px; border: 1px solid transparent; transition: all 0.3s;
        display: flex; align-items: center; justify-content: space-between;
    }}
    .playlist-item:hover {{ 
        background: rgba(255, 255, 255, 0.08); 
        transform: translateX(5px); 
        border-color: rgba(255, 255, 255, 0.1);
    }}
    .playlist-item.active {{
        background: linear-gradient(90deg, var(--primary-dim), rgba(0,0,0,0));
        border-left: 4px solid var(--primary-color);
    }}
    
    /* Hide ugly audio element */
    .stAudio {{ display: none; }}
    
    /* COLOR PICKER STYLING */
    div[data-testid="stColorPicker"] > div > label > div {{
        background: black !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- INJECT BACKGROUND ORBS ----------------
st.markdown("""
<div class="bg-gradient"></div>
<div class="blob blob-1"></div>
<div class="blob blob-2"></div>
""", unsafe_allow_html=True)

# ---------------- START SCREEN ----------------
if not st.session_state.user_interacted:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class="start-screen-container">
            <div class="start-title">SONICSTREAM</div>
            <p style="color: rgba(255,255,255,0.5); font-family: 'Rajdhani'; margin-bottom: 60px; letter-spacing: 2px;">IMMERSIVE AUDIO SYSTEM</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ INITIALIZE SYSTEM", key="start_btn", type="primary"):
            st.session_state.user_interacted = True
            st.rerun()
    st.stop()

# ---------------- HEADER ----------------
st.markdown("""
<div class="glass-card" style="text-align: center; padding: 20px;">
    <h1 style="margin: 0; font-family: 'Rajdhani'; font-size: 36px; letter-spacing: 2px; color: white;">SonicStream</h1>
</div>
""", unsafe_allow_html=True)

# ---------------- THEME SETTINGS (USER CHOICE COLOR) ----------------
with st.expander("🎨 Theme Settings"):
    st.markdown("<p style='opacity:0.7; font-size:14px;'>Choose your accent color for the interface:</p>", unsafe_allow_html=True)
    new_color = st.color_picker("Accent Color", st.session_state.accent_color)
    if new_color != st.session_state.accent_color:
        st.session_state.accent_color = new_color
        st.rerun()

# ---------------- MODE SELECTOR ----------------
mode = st.radio(
    "",
    ["📤 Upload", "📁 Folder"],
    horizontal=True,
    label_visibility="collapsed"
)

# ---------------- LOAD LOGIC ----------------
uploaded_files = None 

if mode == "📤 Upload":
    st.markdown("""
    <div style="text-align: center; padding: 40px; border: 1px dashed rgba(255,255,255,0.2); border-radius: 20px; margin-bottom: 20px; background: rgba(0,0,0,0.4);">
        <span style="font-size: 40px; filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));">📂</span>
        <p style="margin: 15px 0 0 0; opacity: 0.6; letter-spacing: 1px;">UPLOAD YOUR TRACKS</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "", type=["wav", "mp3", "ogg"], accept_multiple_files=True, label_visibility="collapsed", key="file_uploader_state"
    )
    if uploaded_files:
        st.session_state.playlist = [{"name": f.name} for f in uploaded_files]
        
else:
    music_folder = "music"
    if not os.path.isdir(music_folder):
        st.warning("Folder 'music' not found.")
    else:
        files = [f for f in os.listdir(music_folder) if f.lower().endswith((".wav", ".mp3"))]
        if files:
            st.session_state.playlist = [{"name": f} for f in files]

# ---------------- PLAYER UI ----------------
if st.session_state.playlist:
    current_song_info = st.session_state.playlist[st.session_state.current_song_index]
    song_name = current_song_info["name"]
    
    # Dynamic Audio Loading
    audio_data = None
    audio_format = "audio/mp3"
    
    if mode == "📤 Upload":
        if uploaded_files:
            target_file = next((f for f in uploaded_files if f.name == song_name), None)
            if target_file:
                audio_data = target_file.read()
                audio_format = target_file.type
    else:
        music_folder = "music"
        path = os.path.join(music_folder, song_name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                audio_data = f.read()
                audio_format = f"audio/{song_name.split('.')[-1].lower()}"
    
    if not audio_data:
        st.error(f"Could not load audio for: {song_name}")
    else:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        # Album Art (Styled)
        art_state = "" if st.session_state.is_playing else "paused"
        st.markdown(f"""
        <div style="position: relative; width: 260px; height: 260px; margin: 0 auto 30px; display: flex; align-items: center; justify-content: center;">
            <div style="position: absolute; width: 100%; height: 100%; border-radius: 50%; background: #111; opacity: 0.5; filter: blur(30px);"></div>
            <div style="position: relative; z-index: 2; width: 100%; height: 100%; border-radius: 50%; background: #000; display: flex; align-items: center; justify-content: center; font-size: 100px; box-shadow: 0 0 40px rgba(0,0,0,1), inset 0 0 0 1px #333; animation: rotate 30s linear infinite;" class="album-art {art_state}">
                🎵
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Song Info (Styled)
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <div class="song-title">{song_name}</div>
            <p style="margin: 5px 0 0 0; opacity: 0.6; font-family: 'Rajdhani'; font-size: 16px; letter-spacing: 1px;">
                {'NOW PLAYING' if st.session_state.is_playing else 'PAUSED'}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Visualizer (Styled)
        vis_state = "" if st.session_state.is_playing else "paused"
        bars = "".join([
            f'<div class="visualizer-bar" style="--bar-height: {random.randint(20, 80)}px; animation-duration: {random.uniform(0.8, 1.5)}s; animation-delay: {random.uniform(0, 0.5)}s"></div>' 
            for i in range(30)
        ])
        st.markdown(f"""
        <div class="visualizer-container {vis_state}">
            {bars}
        </div>
        """, unsafe_allow_html=True)
        
        # Controls (Stylish Deck)
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1.5, 1, 1])
        
        with c1:
            if st.button("⏮", key="btn_prev"):
                st.session_state.current_song_index = (st.session_state.current_song_index - 1) % len(st.session_state.playlist)
                st.session_state.is_playing = True
                st.rerun()
        with c2:
            if st.button("🔀", key="btn_shuffle"):
                st.session_state.shuffle = not st.session_state.shuffle
                if st.session_state.shuffle:
                    random.shuffle(st.session_state.playlist)
                    st.session_state.current_song_index = 0
                st.rerun()
        with c3:
            play_icon = "⏸" if st.session_state.is_playing else "▶"
            if st.button(play_icon, key="btn_play", use_container_width=True):
                st.session_state.is_playing = not st.session_state.is_playing
                st.rerun()
        with c4:
            if st.button("🔁", key="btn_repeat"):
                st.session_state.repeat = not st.session_state.repeat
                st.rerun()
        with c5:
            if st.button("⏭", key="btn_next"):
                st.session_state.current_song_index = (st.session_state.current_song_index + 1) % len(st.session_state.playlist)
                st.session_state.is_playing = True
                st.rerun()
                
        # Volume
        vol = st.slider("Volume", 0.0, 1.0, st.session_state.volume, label_visibility="collapsed")
        st.session_state.volume = vol
        
        # Audio Logic
        if st.session_state.is_playing:
            st.audio(audio_data, format=audio_format, start_time=st.session_state.start_time, autoplay=True)
        else:
            st.audio(audio_data, format=audio_format, start_time=st.session_state.start_time, autoplay=False)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Playlist
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin:0 0 20px 0; font-family: Rajdhani; font-size: 22px; color: rgba(255,255,255,0.8);">UP NEXT</h3>', unsafe_allow_html=True)
    
    for i, song in enumerate(st.session_state.playlist):
        active = "active" if i == st.session_state.current_song_index else ""
        col_song, col_btn = st.columns([5, 1])
        with col_song:
            st.markdown(f'<div class="playlist-item {active}"><span style="font-size: 12px; opacity: 0.5; margin-right: 15px; font-family: Rajdhani;">{str(i+1).zfill(2)}</span> {song["name"]}</div>', unsafe_allow_html=True)
        with col_btn:
            if st.button("▶", key=f"btn_play_list_{i}"):
                st.session_state.current_song_index = i
                st.session_state.is_playing = True
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 60px;">
        <h2 style="opacity: 0.5; font-family: Rajdhani;">NO AUDIO SOURCE</h2>
        <p style="opacity: 0.3;">Select files or folder to begin playback.</p>
    </div>
    """, unsafe_allow_html=True)
