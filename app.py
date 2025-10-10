import streamlit as st
import pickle
import pandas as pd
import requests
import numpy as np

# -------------------------------
# TMDB API Key (your given one)
# -------------------------------
API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# -------------------------------
# Function to fetch movie poster
# -------------------------------
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster+Found"

    except Exception as e:
        print(f"Error fetching poster for movie_id {movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=Poster+Unavailable"

# -------------------------------
# Load movie data and similarity
# -------------------------------
st.title('🎬 Movie Recommender System')

try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
except Exception as e:
    st.error(f"Error loading movie dictionary: {e}")
    st.stop()

try:
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except MemoryError:
    st.error("❌ Not enough memory to load similarity matrix. Try using a smaller dataset or rebuild it efficiently.")
    st.stop()
except Exception as e:
    st.error(f"Error loading similarity data: {e}")
    st.stop()

# -------------------------------
# Recommend movies function
# -------------------------------
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    
    # Handle NumPy memory issues gracefully
    if not isinstance(distances, np.ndarray):
        distances = np.array(distances)
    
    # Get top 5 similar movies
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# -------------------------------
# Streamlit UI
# -------------------------------
selected_movie_name = st.selectbox(
    '🎥 Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    with st.spinner('Fetching recommendations...'):
        names, posters = recommend(selected_movie_name)

    if len(names) == 0:
        st.warning("No recommendations found. Try another movie.")
    else:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if idx < len(names):
                with col:
                    st.text(names[idx])
                    st.image(posters[idx])




