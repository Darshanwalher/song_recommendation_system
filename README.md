# 🎵 Spotify Song Recommendation System

## 📌 Overview  
This is a **content-based music recommendation system** that suggests songs similar to your favorite tracks using machine learning. It analyzes various audio features to deliver personalized recommendations that match your musical taste and mood.

---

## ✨ Features  
- 🎯 **Personalized Recommendations**  
  Suggests 5 songs based on the selected track.

- 🎧 **Spotify Integration**  
  Fetches album covers, artist info, and song previews directly from the Spotify API.

- 🔊 **Audio Previews**  
  Listen to 30-second audio clips of recommended tracks.

- 📋 **Detailed Song Information**  
  View artist name, album title, release year, and popularity.

- 💻 **Responsive Design**  
  Fully functional on both desktop and mobile devices.

---

## 🛠️ Technologies Used  
- **Python**  
- **Streamlit** – Web app frontend  
- **Spotipy** – Spotify Web API wrapper  
- **Scikit-learn** – K-Nearest Neighbors (KNN) algorithm  
- **Pickle** – For model serialization  

---

## 🔍 How It Works  
1. Uses the **KNN algorithm** to find songs with similar audio characteristics.  
2. Audio features include:  
   - Danceability  
   - Energy  
   - Tempo  
   - Acousticness  
   - Valence  
3. Based on the selected song, the app retrieves the most similar songs.  
4. It then uses the Spotify API to display song previews, album art, and metadata.

---

## 🚀 Live Demo  
- 🌐 [Render Deployment](https://spotify-song-recommendation-system.onrender.com)  
- 🌐 [Streamlit Cloud Deployment](https://songrecommendationsystem-clwjppwpvkgesdxpjntryj.streamlit.app/)

---

## 📦 Installation  

To run the project locally:

### 1. Clone the repository:
```bash
git clone https://github.com/yourusername/spotify-song-recommendation-system.git
cd spotify-song-recommendation-system
