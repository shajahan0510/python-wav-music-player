import streamlit as st
import os
import time
import base64
from io import BytesIO
import random

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Advanced Music Player",
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
if 'mobile_detected' not in st.session_state:
    st.session_state.mobile_detected = False
if 'user_interacted' not in st.session_state:
    st.session_state.user_interacted = False

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        min-height: 100vh;
        margin: 0;
        padding: 0;
    }
    
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        width: 100%;
        box-sizing: border-box;
    }
    
    .player-header {
        text-align: center;
        margin-bottom: 30px;
        animation: fadeInDown 1s ease;
    }
    
    .player-header h1 {
        font-size: 36px;
        font-weight: 700;
        background: linear-gradient(45deg, #00d2ff, #3a7bd5, #00d2ff);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease infinite;
        margin: 0;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    .album-art {
        width: 200px;
        height: 200px;
        margin: 0 auto 20px;
        border-radius: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 80px;
        position: relative;
        overflow: hidden;
        animation: rotate 20s linear infinite;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
    }
    
    .album-art.paused {
        animation-play-state: paused;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .album-art::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .song-info {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .song-title {
        font-size: 22px;
        font-weight: 600;
        color: white;
        margin-bottom: 10px;
        word-wrap: break-word;
    }
    
    .song-artist {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .visualizer-container {
        height: 60px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 3px;
        margin: 20px 0;
        padding: 15px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
    }
    
    .visualizer-bar {
        width: 5px;
        background: linear-gradient(to top, #00d2ff, #3a7bd5);
        border-radius: 3px;
        animation: wave 1s ease-in-out infinite;
        transition: all 0.3s ease;
    }
    
    .visualizer-container.paused .visualizer-bar {
        animation-play-state: paused;
        opacity: 0.5;
    }
    
    @keyframes wave {
        0%, 100% { height: 10px; }
        50% { height: var(--bar-height); }
    }
    
    .progress-section {
        margin: 20px 0;
    }
    
    .progress-bar {
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
        cursor: pointer;
        position: relative;
    }
    
    .progress-fill {
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        border-radius: 3px;
        transition: width 0.3s ease;
        position: relative;
    }
    
    .progress-fill::after {
        content: '';
        position: absolute;
        right: -8px;
        top: 50%;
        transform: translateY(-50%);
        width: 12px;
        height: 12px;
        background: white;
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
    }
    
    .time-info {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        color: rgba(255, 255, 255, 0.7);
        font-size: 14px;
    }
    
    .controls {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin: 20px 0;
    }
    
    .control-btn {
        background: rgba(255, 255, 255, 0.1);
        border: none;
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 18px;
    }
    
    .control-btn:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.1);
    }
    
    .control-btn.play-pause {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        font-size: 24px;
        box-shadow: 0 5px 20px rgba(0, 210, 255, 0.4);
    }
    
    .control-btn.play-pause:hover {
        box-shadow: 0 8px 30px rgba(0, 210, 255, 0.6);
    }
    
    .volume-control {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 20px 0;
        padding: 15px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
    }
    
    .volume-slider {
        flex: 1;
        -webkit-appearance: none;
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        outline: none;
    }
    
    .volume-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 16px;
        height: 16px;
        background: white;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0, 210, 255, 0.5);
    }
    
    .playlist-section {
        margin-top: 20px;
        max-height: 250px;
        overflow-y: auto;
    }
    
    .playlist-header {
        font-size: 18px;
        font-weight: 600;
        color: white;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .playlist-item {
        padding: 12px;
        margin: 8px 0;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .playlist-item:hover {
        background: rgba(0, 210, 255, 0.1);
        transform: translateX(10px);
    }
    
    .playlist-item.active {
        background: linear-gradient(135deg, rgba(0, 210, 255, 0.2), rgba(58, 123, 213, 0.2));
        border-left: 3px solid #00d2ff;
    }
    
    .playlist-number {
        width: 30px;
        height: 30px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .playlist-item.active .playlist-number {
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        color: white;
    }
    
    .upload-section {
        border: 2px dashed rgba(0, 210, 255, 0.3);
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        background: rgba(0, 210, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #00d2ff;
        background: rgba(0, 210, 255, 0.1);
    }
    
    .mode-selector {
        display: flex;
        gap: 10px;
        margin: 20px 0;
        background: rgba(0, 0, 0, 0.2);
        padding: 5px;
        border-radius: 10px;
    }
    
    .mode-btn {
        flex: 1;
        padding: 12px;
        background: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.7);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .mode-btn.active {
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        color: white;
    }
    
    .status-bar {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin: 20px 0;
        padding: 12px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        flex-wrap: wrap;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        font-size: 14px;
        color: rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
    }
    
    .status-item:hover {
        background: rgba(0, 210, 255, 0.1);
        transform: scale(1.05);
    }
    
    .empty-state {
        text-align: center;
        padding: 40px;
        color: rgba(255, 255, 255, 0.6);
    }
    
    .empty-state-icon {
        font-size: 60px;
        margin-bottom: 15px;
        opacity: 0.5;
    }
    
    /* Mobile audio fix */
    .mobile-audio-container {
        position: relative;
        width: 100%;
        margin-top: 20px;
    }
    
    .mobile-play-btn {
        display: none;
        width: 100%;
        padding: 15px;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .mobile-play-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 210, 255, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 210, 255, 0.5);
    }
    
    /* Hide default audio controls */
    audio {
        display: none;
    }
    
    /* Custom audio player container */
    .custom-audio-container {
        position: relative;
        width: 100%;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-container {
            padding: 10px;
        }
        
        .player-header h1 {
            font-size: 28px;
        }
        
        .album-art {
            width: 150px;
            height: 150px;
            font-size: 60px;
        }
        
        .song-title {
            font-size: 18px;
        }
        
        .song-artist {
            font-size: 14px;
        }
        
        .visualizer-container {
            height: 40px;
            padding: 10px;
        }
        
        .visualizer-bar {
            width: 3px;
        }
        
        .control-btn {
            width: 40px;
            height: 40px;
            font-size: 14px;
        }
        
        .control-btn.play-pause {
            width: 50px;
            height: 50px;
            font-size: 20px;
        }
        
        .controls {
            gap: 10px;
        }
        
        .status-bar {
            gap: 10px;
        }
        
        .status-item {
            padding: 6px 10px;
            font-size: 12px;
        }
        
        .mobile-play-btn {
            display: block;
        }
        
        .playlist-section {
            max-height: 200px;
        }
        
        .playlist-item {
            padding: 10px;
        }
        
        .upload-section {
            padding: 20px;
        }
    }
    
    @media (max-width: 480px) {
        .player-header h1 {
            font-size: 24px;
        }
        
        .album-art {
            width: 120px;
            height: 120px;
            font-size: 50px;
        }
        
        .song-title {
            font-size: 16px;
        }
        
        .song-artist {
            font-size: 12px;
        }
        
        .visualizer-container {
            height: 30px;
            padding: 8px;
        }
        
        .visualizer-bar {
            width: 2px;
        }
        
        .control-btn {
            width: 35px;
            height: 35px;
            font-size: 12px;
        }
        
        .control-btn.play-pause {
            width: 45px;
            height: 45px;
            font-size: 18px;
        }
        
        .controls {
            gap: 8px;
        }
        
        .status-bar {
            gap: 8px;
        }
        
        .status-item {
            padding: 5px 8px;
            font-size: 11px;
        }
        
        .volume-control {
            padding: 10px;
        }
        
        .playlist-section {
            max-height: 150px;
        }
        
        .playlist-item {
            padding: 8px;
        }
        
        .upload-section {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown("""
<div class="main-container">
    <div class="player-header">
        <h1>🎵 Advanced Music Player</h1>
        <p style="color: rgba(255,255,255,0.7); margin-top: 10px;">Immersive Audio Experience</p>
    </div>
""", unsafe_allow_html=True)

# ---------------- Mode Selection ----------------
st.markdown("""
    <div class="mode-selector">
        <button class="mode-btn active">📤 Upload</button>
        <button class="mode-btn">📁 Folder</button>
    </div>
    """, unsafe_allow_html=True)
    
mode = st.radio(
    "",
    ["📤 Upload playlist", "📁 Use music folder"],
    horizontal=True,
    label_visibility="collapsed"
)

# ---------------- Load Playlist ----------------
if mode == "📤 Upload playlist":
    st.markdown("""
    <div class="upload-section">
        <div style="font-size: 48px; margin-bottom: 15px;">📁</div>
        <p style="font-size: 18px; color: rgba(255,255,255,0.9); margin-bottom: 10px;">Drop your music files here</p>
        <p style="font-size: 14px; color: rgba(255,255,255,0.5);">MP3, WAV supported</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "",
        type=["wav", "mp3"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.session_state.playlist = []
        for f in uploaded_files:
            st.session_state.playlist.append({
                "name": f.name,
                "bytes": f.read(),
                "format": f.type,
                "size": f.size
            })

else:
    music_folder = "music"

    if not os.path.isdir(music_folder):
        st.error("❌ 'music' folder not found")
    else:
        files = [
            f for f in os.listdir(music_folder)
            if f.lower().endswith((".wav", ".mp3"))
        ]

        if not files:
            st.warning("No audio files found")
        else:
            st.session_state.playlist = []
            for f in files:
                path = os.path.join(music_folder, f)
                with open(path, "rb") as audio:
                    st.session_state.playlist.append({
                        "name": f,
                        "bytes": audio.read(),
                        "format": f"audio/{f.split('.')[-1].lower()}",
                        "size": os.path.getsize(path)
                    })

# ---------------- Player UI ----------------
if st.session_state.playlist:
    current_song = st.session_state.playlist[st.session_state.current_song_index]
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Album Art
    album_class = "" if st.session_state.is_playing else "paused"
    st.markdown(f"""
    <div class="album-art {album_class}">
        🎵
    </div>
    """, unsafe_allow_html=True)
    
    # Song Info
    st.markdown(f"""
    <div class="song-info">
        <div class="song-title">{current_song['name']}</div>
        <div class="song-artist">{'Now Playing' if st.session_state.is_playing else 'Paused'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualizer
    visualizer_class = "" if st.session_state.is_playing else "paused"
    bars = "".join([
        f'<div class="visualizer-bar" style="--bar-height: {random.randint(20, 70)}px; animation-delay: {i*0.05}s"></div>' 
        for i in range(30)  # Reduced bars for mobile
    ])
    st.markdown(f"""
    <div class="visualizer-container {visualizer_class}">
        {bars}
    </div>
    """, unsafe_allow_html=True)
    
    # Progress Bar
    st.markdown("""
    <div class="progress-section">
        <div class="progress-bar">
            <div class="progress-fill" style="width: 35%;"></div>
        </div>
        <div class="time-info">
            <span>1:23</span>
            <span>3:45</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1.5, 1, 1])
    
    with col1:
        if st.button("⏮", key="btn_prev"):
            st.session_state.current_song_index = (st.session_state.current_song_index - 1) % len(st.session_state.playlist)
            st.session_state.is_playing = True
            st.session_state.start_time = 0
            st.session_state.user_interacted = True
            st.rerun()
    
    with col2:
        if st.button("🔀", key="btn_shuffle"):
            st.session_state.shuffle = not st.session_state.shuffle
            if st.session_state.shuffle:
                random.shuffle(st.session_state.playlist)
                st.session_state.current_song_index = 0
            st.rerun()
    
    with col3:
        play_icon = "⏸" if st.session_state.is_playing else "▶"
        if st.button(play_icon, key="btn_play", use_container_width=True):
            st.session_state.is_playing = not st.session_state.is_playing
            st.session_state.user_interacted = True
            if st.session_state.is_playing:
                st.session_state.start_time = 0
            st.rerun()
    
    with col4:
        if st.button("🔁", key="btn_repeat"):
            st.session_state.repeat = not st.session_state.repeat
            st.rerun()
    
    with col5:
        if st.button("⏭", key="btn_next"):
            st.session_state.current_song_index = (st.session_state.current_song_index + 1) % len(st.session_state.playlist)
            st.session_state.is_playing = True
            st.session_state.start_time = 0
            st.session_state.user_interacted = True
            st.rerun()
    
    # Volume Control
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.write("🔊")
    with col2:
        volume = st.slider(
            "Volume",
            0.0, 1.0, st.session_state.volume,
            label_visibility="visible"
        )
        st.session_state.volume = volume
    with col3:
        st.write("")
    
    # Mobile Audio Fix
    st.markdown('<div class="mobile-audio-container">', unsafe_allow_html=True)
    
    # Create a base64 encoded version of the audio for mobile compatibility
    audio_data = current_song["bytes"]
    b64 = base64.b64encode(audio_data).decode()
    
    # Custom HTML5 audio player for mobile
    st.markdown(f"""
    <audio id="audio-player" controls style="width: 100%; margin-top: 10px;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
    """, unsafe_allow_html=True)
    
    # JavaScript to handle mobile audio playback
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const audio = document.getElementById('audio-player');
        const playBtn = document.querySelector('[data-testid="stButton"]'); // This might need adjustment
        
        // Function to play audio
        function playAudio() {
            const playPromise = audio.play();
            
            if (playPromise !== undefined) {
                playPromise.then(_ => {
                    // Autoplay started
                    console.log('Audio playing');
                }).catch(error => {
                    // Autoplay was prevented
                    console.log('Autoplay prevented:', error);
                });
            }
        }
        
        // Check if it's a mobile device
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        
        if (isMobile) {
            // Show custom play button for mobile
            const mobilePlayBtn = document.createElement('button');
            mobilePlayBtn.textContent = '▶ Play Audio';
            mobilePlayBtn.className = 'mobile-play-btn';
            
            mobilePlayBtn.addEventListener('click', function() {
                playAudio();
            });
            
            // Insert the button after the audio element
            audio.parentNode.insertBefore(mobilePlayBtn, audio.nextSibling);
        }
        
        // Try to play audio when user interacts with the page
        document.addEventListener('click', function() {
            if (audio.paused) {
                playAudio();
            }
        }, { once: true });
    });
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Regular Streamlit audio element for desktop
    st.markdown('<div class="custom-audio-container">', unsafe_allow_html=True)
    
    if st.session_state.is_playing and st.session_state.user_interacted:
        # When playing, show audio with autoplay
        st.audio(
            audio_data,
            format=current_song["format"],
            start_time=st.session_state.start_time,
            autoplay=True
        )
    else:
        # When paused, still show the audio but without autoplay
        st.audio(
            audio_data,
            format=current_song["format"],
            start_time=st.session_state.start_time,
            autoplay=False
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Status Bar
    status_items = []
    if st.session_state.shuffle:
        status_items.append('<div class="status-item">🔀 Shuffle</div>')
    if st.session_state.repeat:
        status_items.append('<div class="status-item">🔁 Repeat</div>')
    if st.session_state.is_playing:
        status_items.append('<div class="status-item">▶ Playing</div>')
    else:
        status_items.append('<div class="status-item">⏸ Paused</div>')
    
    st.markdown(f"""
    <div class="status-bar">
        {''.join(status_items)}
    </div>
    """, unsafe_allow_html=True)
    
    # Playlist
    st.markdown('<div class="glass-card playlist-section">', unsafe_allow_html=True)
    st.markdown('<div class="playlist-header">📋 Playlist</div>', unsafe_allow_html=True)
    
    for i, song in enumerate(st.session_state.playlist):
        is_active = i == st.session_state.current_song_index
        
        if st.button(
            f"{'🎵' if is_active else '🎶'} {song['name']}",
            key=f"song_btn_{i}",
            help=f"Play {song['name']}",
            use_container_width=True
        ):
            st.session_state.current_song_index = i
            st.session_state.is_playing = True
            st.session_state.start_time = 0
            st.session_state.user_interacted = True
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="glass-card empty-state">
        <div class="empty-state-icon">🎵</div>
        <h3>No Music Available</h3>
        <p>Upload your favorite songs to get started</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
