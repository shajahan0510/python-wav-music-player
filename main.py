import streamlit as st
import os

# Page settings
st.set_page_config(
    page_title="WAV Music Player",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 WAV Music Player")
st.write("Select a WAV file and play it directly in your browser.")

# Music folder
music_folder = "music"

# Check folder
if not os.path.isdir(music_folder):
    st.error("❌ 'music' folder not found")
    st.stop()

# Load songs
songs = [f for f in os.listdir(music_folder) if f.lower().endswith(".wav")]

if not songs:
    st.warning("⚠️ No WAV files found in the music folder")
    st.stop()

# Song selector
selected_song = st.selectbox("🎧 Choose a song", songs)

file_path = os.path.join(music_folder, selected_song)

# Play audio
with open(file_path, "rb") as audio_file:
    st.audio(audio_file.read(), format="audio/wav")

st.success("▶️ Playing in browser")

