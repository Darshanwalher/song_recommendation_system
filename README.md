🎵 Spotify Song Recommendation System
📌 Overview
This project is a content-based music recommendation system that suggests songs similar to your favorite tracks. Using machine learning algorithms, it analyzes audio features to find songs with similar characteristics, providing personalized recommendations.

✨ Features
Personalized Recommendations: Get 5 songs similar to your favorite track

Spotify Integration: Fetches album covers and song previews directly from Spotify

Audio Previews: Listen to 30-second previews of recommended songs

Detailed Song Information: View album, artist, release year, and popularity

Responsive Design: Works seamlessly on desktop and mobile devices

🛠️ Technologies Used
Python

Streamlit (Frontend)

Spotipy (Spotify API wrapper)

Scikit-learn (K-Nearest Neighbors algorithm)

Pickle (Model serialization)

🔍 How It Works
The system uses K-Nearest Neighbors algorithm to find songs with similar audio features

Audio features include danceability, energy, tempo, acousticness, etc.

When you select a song, it finds the most similar tracks in the dataset

The app then fetches additional metadata (cover art, previews) from Spotify API

🚀 Demo Links
Render Deployment

Streamlit Cloud Deployment

📦 Installation
To run this project locally:

Clone the repository:

bash
git clone https://github.com/yourusername/spotify-song-recommender.git
cd spotify-song-recommender
Install dependencies:

bash
pip install -r requirements.txt
Set up Spotify API credentials:

Create an app on Spotify Developer Dashboard

Add your CLIENT_ID and CLIENT_SECRET to the code

Run the app:

bash
streamlit run app.py
📂 Project Structure
text
├── app.py                # Main application file
├── df.pkl                # Processed song dataset
├── matrix.pkl            # Feature matrix
├── NN_model.pkl          # Trained model
├── requirements.txt      # Dependencies
└── README.md             # Project documentation
📝 Future Enhancements
Add user authentication to save preferences

Implement collaborative filtering

Create playlists from recommendations

Add mood-based filtering

Include more detailed audio analysis
