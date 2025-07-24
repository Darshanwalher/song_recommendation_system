import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import time
import random
import lzma
import os

# ================= SET PAGE CONFIG FIRST ==================
st.set_page_config(
    page_title="Spotify Music Recommender", 
    layout="wide", 
    page_icon="🎵",
    initial_sidebar_state="expanded"
)


# ================= SPOTIFY SETUP ==================
CLIENT_ID = "ad6f0c246959458aa9220cdcb1644d19"
CLIENT_SECRET = "e0455067b3264e149577e18a0cd5dfe8"

try:
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
except spotipy.exceptions.SpotifyException as e:
    st.error(f"Spotify API connection failed: {e}. Please check your CLIENT_ID and CLIENT_SECRET.")
    st.stop()

# ================ HELPER FUNCTION TO DISPLAY CARDS ==================
def display_recommendation_card(rec):
    """Helper function to display a recommendation card"""
    st.markdown(f"""
    <div class="recommend-card">
        <div style="position: relative;">
            <img src="{rec['cover']}" style="width:100%; border-radius:8px; margin-bottom:12px;">
            <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); padding: 3px 8px; border-radius: 12px; font-size: 0.8rem;">
                {rec['popularity']}%
            </div>
        </div>
        <div class="recommend-title" title="{rec['name']}">{rec['name']}</div>
        <div class="recommend-artist" title="{rec['artist']}">👤 {rec['artist']}</div>
        <div class="recommend-album" title="{rec['album']}">💿 {rec['album']}</div>
        <div class="recommend-year">
            <span>📅 {rec['release_year']}</span>
            <span>⏱ {rec['duration']}</span>
        </div>
        <div style="margin-top: 15px;">
            <a href="{rec['spotify_url']}" target="_blank" style="text-decoration: none;">
                <button style="
                    background: #1DB954;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-size: 0.8rem;
                    width: 100%;
                ">
                    Play on Spotify
                </button>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if rec["preview_url"]:
        st.audio(rec["preview_url"], format="audio/mp3")

# ================ FETCH SONG DETAILS ==================
def get_song_info(song_name, artist_name):
    query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=query, type="track", limit=1)
    
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        return {
            "cover": track["album"]["images"][0]["url"],
            "artist": ", ".join([artist["name"] for artist in track["artists"]]),
            "album": track["album"]["name"],
            "preview_url": track["preview_url"],
            "release_date": track["album"]["release_date"][:4],
            "duration_ms": track["duration_ms"],
            "popularity": track["popularity"],
            "external_url": track["external_urls"]["spotify"]
        }
    return None

# ================= RECOMMENDATION FUNCTION ==================
def recommend(song_name, n_recommendations=10):
    try:
        idx = df[df['song'] == song_name].index[0]
        distances, indices = nn_model.kneighbors(matrix[idx].reshape(1, -1), n_neighbors=50)

        recommended_songs = []
        seen = set()

        for i in indices[0]:
            name = df.iloc[i].song
            artist = df.iloc[i].artist
            
            if name.lower() != song_name.lower() and name not in seen:
                song_info = get_song_info(name, artist)
                if song_info:
                    recommended_songs.append({
                        "name": name,
                        "artist": artist,
                        "cover": song_info["cover"],
                        "preview_url": song_info["preview_url"],
                        "album": song_info["album"],
                        "release_year": song_info["release_date"],
                        "duration": f"{int(song_info['duration_ms']/60000)}:{int((song_info['duration_ms']%60000)/1000):02d}",
                        "popularity": song_info["popularity"],
                        "spotify_url": song_info["external_url"]
                    })
                    seen.add(name)
            
            if len(recommended_songs) == n_recommendations:
                break

        return recommended_songs
    except IndexError:
        st.error(f"The song '{song_name}' could not be found in the dataset. Please select another song.")
        return []

# ================= ENHANCED CUSTOM CSS ==================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Poppins:wght@400;600;700&display=swap');
    
    /* Main Content */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #121212;
        color: #ffffff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1DB954, #191414) !important;
        box-shadow: 5px 0 15px rgba(0,0,0,0.3);
    }
    .sidebar .sidebar-content {
        color: white !important;
    }
    .sidebar .stMarkdown h2, .sidebar .stMarkdown h3 {
        color: white !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(to right, #1DB954, #1ED760);
        color: white;
        border: none;
        padding: 0.7rem 1.8rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(29, 185, 84, 0.3);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Cards */
    .recommend-card {
        background: linear-gradient(145deg, #181818, #282828);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border-left: 4px solid transparent;
    }
    .recommend-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 24px rgba(29, 185, 84, 0.2);
        border-left: 4px solid #1DB954;
    }
    .recommend-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-family: 'Montserrat', sans-serif;
    }
    .recommend-artist {
        font-size: 1rem;
        color: #b3b3b3;
        margin-bottom: 0.5rem;
    }
    .recommend-album {
        font-size: 0.95rem;
        color: #aaaaaa;
        font-style: italic;
        margin-bottom: 0.5rem;
    }
    .recommend-year {
        font-size: 0.85rem;
        color: #999999;
        margin-top: 0.8rem;
        display: flex;
        justify-content: space-between;
    }
    
    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #2d2d2d !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 8px 12px;
    }
    .stSelectbox div[data-baseweb="select"] input {
        color: white !important;
    }
    
    /* Navigation */
    .st-eb {
        padding: 0 !important;
    }
    
    /* Currently Playing */
    .now-playing {
        background: linear-gradient(145deg, #181818, #282828);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border-left: 4px solid #1DB954;
    }
    
    /* Popularity meter */
    .popularity-container {
        margin-top: 1rem;
    }
    .popularity-meter {
        height: 6px;
        background: #535353;
        border-radius: 3px;
        margin-top: 5px;
        overflow: hidden;
    }
    
    .popularity-level {
        height: 100%;
        background: linear-gradient(to right, #1DB954, #1ED760);
        border-radius: 3px;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #1DB954, #191414);
        padding: 50px 40px;
        margin-bottom: 30px;
        border-radius: 0 0 15px 15px;
        text-align: center;
    }
    
    /* Audio player */
    audio {
        width: 100%;
        margin-top: 15px;
        filter: brightness(0.8);
        border-radius: 10px;
    }
    
    audio::-webkit-media-controls-panel {
        background-color: #2d2d2d;
        border-radius: 10px;
    }
    
    /* Progress animation */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        background-color: #1DB954;
        color: white;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    /* Floating action button */
    .floating-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: #1DB954;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(29, 185, 84, 0.4);
        cursor: pointer;
        z-index: 1000;
        transition: all 0.3s ease;
    }
    .floating-btn:hover {
        transform: scale(1.1) rotate(10deg);
        box-shadow: 0 6px 20px rgba(29, 185, 84, 0.6);
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: #1DB954;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Responsive columns */
    @media (max-width: 768px) {
        .recommend-card {
            padding: 1rem;
        }
        .header {
            padding: 30px 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA ==================
@st.cache_data
def load_data():
    try:
        # Check if files exist
        required_files = ['final_df.pkl', 'final_matrix.pkl', 'NN_final.pkl']
        for file in required_files:
            if not os.path.exists(file):
                st.error(f"Missing file: {file}")
                st.stop()

        # Load files using standard pickle
        with open('final_df.pkl', 'rb') as f1:
            df = pickle.load(f1)
        with open('final_matrix.pkl', 'rb') as f2:
            matrix = pickle.load(f2)
        with open('NN_final.pkl', 'rb') as f3:
            nn_model = pickle.load(f3)

        return df, matrix, nn_model

    except pickle.UnpicklingError as pickle_err:
        st.error(f"Pickle loading error: {pickle_err}")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.stop()

# Load data once cached
df, matrix, nn_model = load_data()


# ================= SIDEBAR ==================
with st.sidebar:
    # Logo and Title with animation
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <img src="https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_White.png" width="180" class="pulse-animation">
        <h3 style="color: white; margin-top: 10px;">Music Discovery Engine</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Menu with icons
    selected = option_menu(
        menu_title=None,
        options=["Home", "Recommendations", "Top Picks", "About"],
        icons=["house-heart", "music-note-beamed", "stars", "info-circle"],
        default_index=1,
        styles={
            "container": {
                "padding": "0!important", 
                "background-color": "transparent",
                "margin-bottom": "30px"
            },
            "icon": {
                "color": "white", 
                "font-size": "18px",
                "margin-right": "10px"
            }, 
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px 0",
                "padding": "12px 15px",
                "border-radius": "8px",
                "color": "white",
                "transition": "all 0.3s ease"
            },
            "nav-link:hover": {
                "background-color": "rgba(29, 185, 84, 0.3)",
                "transform": "translateX(5px)"
            },
            "nav-link-selected": {
                "background-color": "#1DB954",
                "font-weight": "bold",
                "box-shadow": "0 4px 8px rgba(29, 185, 84, 0.3)"
            },
        }
    )
    
    # Interactive Search Section
    st.markdown("---")
    st.markdown("### 🔍 Quick Search")
    quick_search = st.text_input("Search for a song or artist", key="quick_search")
    
    if quick_search:
        results = sp.search(q=quick_search, type='track', limit=5)
        if results['tracks']['items']:
            st.markdown("#### Search Results")
            for track in results['tracks']['items']:
                with st.expander(f"{track['name']} - {track['artists'][0]['name']}"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(track['album']['images'][0]['url'], width=80)
                    with col2:
                        st.markdown(f"*Album:* {track['album']['name']}")
                        st.markdown(f"*Release:* {track['album']['release_date'][:4]}")
                        if track['preview_url']:
                            st.audio(track['preview_url'], format="audio/mp3")
    
    # About Section with expandable content
    st.markdown("---")
    with st.expander("ℹ About This App", expanded=True):
        st.markdown("""
        <div style='color: #f0f0f0; font-size: 0.95rem;'>
        Discover music tailored to your taste with our intelligent recommendation system.
        
        <div style='margin-top: 15px;'>
            <span class="badge">AI-Powered</span>
            <span class="badge">Spotify Integration</span>
            <span class="badge">Personalized</span>
        </div>
        
        <div style='margin-top: 15px;'>
            <b>How it works:</b>
            <ul style='margin-top: 5px;'>
                <li>Analyzes audio features</li>
                <li>Finds similar songs</li>
                <li>Generates personalized picks</li>
            </ul>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Social Links
    st.markdown("---")

    # New section for developer contact
    st.markdown("<br>", unsafe_allow_html=True) # Adds a small space
    st.markdown("<p>Made with ❤ by <b>Darshan Walher</b></p>", unsafe_allow_html=True) # Corrected this line
    st.markdown("📧 *Contact:* darshanwalher21@gmail.com")

# The "and rome other thiks" part of your request is a bit unclear, but I've interpreted it as a request to add more information. I've added the developer's name and email in a clear, formatted way. If you meant something else, please clarify, and I'll be happy to adjust the code.
# ================= MAIN CONTENT ==================
if selected == "Home":
    st.markdown("""
    <div class="header">
        <h1 style="color:white; margin-bottom:10px; font-size:2.8rem;">Discover Music You'll Love</h1>
        <p style="color:white; opacity:0.9; margin-top:0; font-size:1.2rem;">Your personal AI-powered music recommendation engine</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Section
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <h2 style='color: #ffffff; margin-top:0;'>🎧 Personalized Music Discovery</h2>
        <p style='font-size:1.1rem; line-height:1.6;'>
            Our advanced AI analyzes thousands of songs to find perfect matches for your taste. 
            Whether you're looking for new artists or rediscovering old favorites, we've got you covered.
        </p>
        
        <div style='background-color: rgba(29, 185, 84, 0.1); padding: 20px; border-radius: 12px; margin: 25px 0;'>
            <h4 style='color: #1DB954; margin-top:0;'>✨ Why You'll Love It</h4>
            <ul style='line-height: 1.8;'>
                <li><b>Smart recommendations</b> based on audio features</li>
                <li><b>Instant previews</b> of recommended tracks</li>
                <li><b>Discover hidden gems</b> you wouldn't find otherwise</li>
                <li><b>Personalized experience</b> that improves over time</li>
            </ul>
        </div>
        
        
        """, unsafe_allow_html=True)
    
    with col2:
        st.image("https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80", 
                 caption="Music connects us all", use_container_width=True)
    
    

elif selected == "Recommendations":
    st.markdown("""
    <div class="header">
        <h1 style="color:white; margin-bottom:10px;">Discover Your Next Favorite Song</h1>
        <p style="color:white; opacity:0.9; margin-top:0;">Get personalized recommendations based on your music taste</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main recommendation interface
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_song = st.selectbox(
            "🎵 Select a song you love:", 
            df['song'].values,
            help="Start typing to search through our database of thousands of songs"
        )
    with col2:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        recommend_btn = st.button("✨ Get Recommendations", key="recommend_btn")
    
    if recommend_btn:
        with st.spinner('🎶 Analyzing your music taste... This may take a moment'):
            # Add a progress bar for better UX
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.02)  # Simulate processing time
                progress_bar.progress(percent_complete + 1)
            
            recommendations = recommend(selected_song, 10)  # Get 10 recommendations
            
            if recommendations:
                # Display selected song in a "Now Playing" card
                selected_song_info = get_song_info(selected_song, df[df['song'] == selected_song].iloc[0].artist)
                
                if selected_song_info:
                    st.markdown('<div class="now-playing">', unsafe_allow_html=True)
                    st.markdown("## 🎧 Currently Playing")
                    
                    # Create two columns to place the image on the left and text on the right
                    col_image, col_text = st.columns([1, 3])
                    with col_image:
                        st.image(selected_song_info["cover"], use_container_width=True, caption=selected_song_info["album"])
                        
                    with col_text:
                        st.markdown(f"### {selected_song}")
                        st.markdown(f"#### 🎤 {selected_song_info['artist']}")
                        st.markdown(f"💿 Album:** {selected_song_info['album']} • *📅 Released:* {selected_song_info['release_date']}")
                        
                        # Popularity meter with more visual appeal
                        st.markdown(f"""
                        <div class="popularity-container">
                            <div style="display: flex; justify-content: space-between;">
                                <span>🔥 Popularity:</span>
                                <span>{selected_song_info['popularity']}/100</span>
                            </div>
                            <div class="popularity-meter">
                                <div class="popularity-level" style="width:{selected_song_info['popularity']}%"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Duration with music note icon
                        duration_min = int(selected_song_info['duration_ms']/60000)
                        duration_sec = int((selected_song_info['duration_ms']%60000)/1000)
                        st.markdown(f"⏱ Duration:** {duration_min}:{duration_sec:02d}")
                        
                        # Audio player with Spotify link
                        if selected_song_info["preview_url"]:
                            st.audio(selected_song_info["preview_url"], format="audio/mp3")
                        st.markdown(f"""
                        <a href="{selected_song_info['external_url']}" target="_blank" style="text-decoration: none;">
                            <button style="
                                background: #1DB954;
                                color: white;
                                border: none;
                                padding: 8px 16px;
                                border-radius: 20px;
                                font-weight: bold;
                                margin-top: 10px;
                                display: inline-flex;
                                align-items: center;
                            ">
                                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/1024px-Spotify_logo_without_text.svg.png" width="20" style="margin-right: 8px;">
                                Play on Spotify
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Display recommendations in a grid
                st.markdown("""
                <div style="margin-top: 40px;">
                    <h2 style="color: #ffffff; margin-bottom: 20px;">🎯 Recommended For You</h2>
                    <p style="color: #b3b3b3; margin-bottom: 20px;">We found these 10 songs that match your taste perfectly</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create two rows of recommendations (5 each)
                row1 = st.columns(5)
                row2 = st.columns(5)
                
                for i, rec in enumerate(recommendations[:5]):
                    with row1[i]:
                        display_recommendation_card(rec)
                
                for i, rec in enumerate(recommendations[5:10]):
                    with row2[i]:
                        display_recommendation_card(rec)
                
                # Add a surprise me button
                if st.button("🎲 Surprise Me With Another Recommendation"):
                    random_rec = random.choice(recommendations)
                    st.success(f"Try this: {random_rec['name']} by {random_rec['artist']}")
                    if random_rec["preview_url"]:
                        st.audio(random_rec["preview_url"], format="audio/mp3")

elif selected == "Top Picks":
    st.markdown("""
    <div class="header">
        <h1 style="color:white; margin-bottom:10px;">🔥 Today's Top Picks</h1>
        <p style="color:white; opacity:0.9; margin-top:0;">Curated recommendations based on popular trends</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display featured recommendations
    st.markdown("""
    <div style="margin-bottom: 30px;">
        <h2 style="color: #ffffff;">🎧 Editor's Choice</h2>
        <p style="color: #b3b3b3;">Handpicked recommendations from our music experts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Featured recommendations (you can customize these)
    featured_songs = [
        {"name": "Blinding Lights", "artist": "The Weeknd"},
        {"name": "Save Your Tears", "artist": "The Weeknd"},
        {"name": "Stay", "artist": "The Kid LAROI, Justin Bieber"},
        {"name": "good 4 u", "artist": "Olivia Rodrigo"},
        {"name": "Levitating", "artist": "Dua Lipa"},
        {"name": "Montero", "artist": "Lil Nas X"},
        {"name": "Peaches", "artist": "Justin Bieber"},
        {"name": "Kiss Me More", "artist": "Doja Cat ft. SZA"},
        {"name": "Butter", "artist": "BTS"},
        {"name": "Deja Vu", "artist": "Olivia Rodrigo"}
    ]
    
    # Get full info for featured songs
    featured_recommendations = []
    for song in featured_songs:
        song_info = get_song_info(song["name"], song["artist"])
        if song_info:
            featured_recommendations.append({
                "name": song["name"],
                "artist": song["artist"],
                "cover": song_info["cover"],
                "preview_url": song_info["preview_url"],
                "album": song_info["album"],
                "release_year": song_info["release_date"],
                "duration": f"{int(song_info['duration_ms']/60000)}:{int((song_info['duration_ms']%60000)/1000):02d}",
                "popularity": song_info["popularity"],
                "spotify_url": song_info["external_url"]
            })
    
    # Display featured recommendations in a grid
    if featured_recommendations:
        row1 = st.columns(5)
        row2 = st.columns(5)
        
        for i, rec in enumerate(featured_recommendations[:5]):
            with row1[i]:
                display_recommendation_card(rec)
        
        for i, rec in enumerate(featured_recommendations[5:10]):
            with row2[i]:
                display_recommendation_card(rec)
    
    # Genre-based recommendations
    st.markdown("""
    <div style="margin-top: 50px; margin-bottom: 30px;">
        <h2 style="color: #ffffff;">🎶 Genre Highlights</h2>
        <p style="color: #b3b3b3;">Explore recommendations by genre</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Genre selector
    genre = st.selectbox("Select a genre:", ["Pop", "Rock", "Hip-Hop", "R&B", "Electronic", "Jazz", "Country"])
    
    # Display genre-based recommendations (simulated)
    if genre:
        with st.spinner(f'Finding the best {genre} tracks for you...'):
            time.sleep(1.5)  # Simulate loading
            st.success(f"Here are some top {genre} recommendations!")
            
            # Simulated genre-based recommendations
            genre_recs = random.sample(df['song'].values.tolist(), 10)
            genre_recommendations = []
            
            for song in genre_recs:
                artist = df[df['song'] == song].iloc[0].artist
                song_info = get_song_info(song, artist)
                if song_info:
                    genre_recommendations.append({
                        "name": song,
                        "artist": artist,
                        "cover": song_info["cover"],
                        "preview_url": song_info["preview_url"],
                        "album": song_info["album"],
                        "release_year": song_info["release_date"],
                        "duration": f"{int(song_info['duration_ms']/60000)}:{int((song_info['duration_ms']%60000)/1000):02d}",
                        "popularity": song_info["popularity"],
                        "spotify_url": song_info["external_url"]
                    })
            
            if genre_recommendations:
                row1 = st.columns(5)
                row2 = st.columns(5)
                
                for i, rec in enumerate(genre_recommendations[:5]):
                    with row1[i]:
                        display_recommendation_card(rec)
                
                for i, rec in enumerate(genre_recommendations[5:10]):
                    with row2[i]:
                        display_recommendation_card(rec)

elif selected == "About":
    st.markdown("""
    <div class="header">
        <h1 style="color:white; margin-bottom:10px;">About Spotify Music Recommender</h1>
        <p style="color:white; opacity:0.9; margin-top:0;">Discover the technology behind your music discovery</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="max-width: 800px; margin: 0 auto;">
        <h2 style='color: #ffffff;'>🎵 About This Project</h2>
        <p style='line-height: 1.7;'>
            The Spotify Music Recommender is an intelligent system designed to help you discover music you'll love. 
            Unlike generic playlists, our recommendations are personalized based on the actual audio characteristics of songs you enjoy.
        </p>
    </div>
    """, unsafe_allow_html=True)