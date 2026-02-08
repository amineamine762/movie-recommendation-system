import streamlit as st
import pickle
import pandas as pd
import ast
import requests
from recommender import recommend

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"  

st.set_page_config(
    page_title="Cinematch | Premium Movie Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css():
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <style>
        .stApp {
            background-color: #141414 !important;
            color: #FFFFFF;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        
        i.fas {
            color: #E50914;
            margin-right: 8px;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #000000;
        }
        
        .title-text {
            font-size: 3.5rem;
            font-weight: 800;
            color: #E50914;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            text-align: center;
        }
        .subtitle-text {
            font-size: 1.2rem;
            color: #B3B3B3;
            margin-bottom: 3rem;
            text-align: center;
        }
        
        .movie-card-container {
            position: relative;
            width: 100%;
            padding-top: 150%; 
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            margin-bottom: 20px;
        }
        
        .movie-card-container:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 20px rgba(0,0,0,0.6);
            border: 2px solid #E50914;
        }
        
        .movie-poster {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: opacity 0.3s ease;
        }
        
        .movie-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            color: white;
            opacity: 0;
            transition: opacity 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 15px;
            text-align: center;
        }
        
        .movie-card-container:hover .movie-overlay {
            opacity: 1;
        }
        
        .overlay-title {
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 10px;
            color: #E50914;
        }
        
        .overlay-info {
            font-size: 0.8rem;
            margin-bottom: 5px;
            color: #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
        }
        
        div[data-baseweb="select"] > div {
            background-color: #333;
            color: white;
            border-radius: 5px;
            border: 1px solid #444;
        }
        
         div.stButton > button {
            background-color: #E50914;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 4px;
            width: 100%;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        div.stButton > button::before {
            content: "\\f0d0"; 
            font-family: "Font Awesome 6 Free";
            font-weight: 900;
            margin-right: 8px;
        }

        div.stButton > button:hover {
            background-color: #F40612;
            box-shadow: 0 4px 12px rgba(229, 9, 20, 0.4);
        }
        
        .metric-container {
            background-color: #1a1a1a;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #333;
            text-align: center;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #E50914;
        }
        .metric-label {
            font-size: 0.8rem;
            color: #aaa;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
        }

    </style>
    """, unsafe_allow_html=True)

local_css()

@st.cache_data
def load_data():
    try:
        new_df = pickle.load(open("artifacts/new_df.pkl", "rb"))
        if not isinstance(new_df, pd.DataFrame):
            new_df = pd.DataFrame(new_df)
    except FileNotFoundError:
        st.error("Error: 'artifacts/new_df.pkl' not found.")
        return pd.DataFrame()

    try:
        movies_metadata = pd.read_csv("data_project/movies.csv")
    except FileNotFoundError:
        st.error("Error: 'data_project/movies.csv' not found.")
        movies_metadata = pd.DataFrame(columns=['id', 'overview', 'vote_average', 'release_date', 'genres', 'popularity'])

    merged_df = pd.merge(
        new_df, 
        movies_metadata[['id', 'overview', 'vote_average', 'release_date', 'genres', 'popularity']], 
        left_on='movie_id', 
        right_on='id', 
        how='left'
    )
    
    def parse_genres(x):
        try:
            if isinstance(x, str):
                return [i['name'] for i in ast.literal_eval(x)]
            return []
        except:
            return []
            
    merged_df['genre_list'] = merged_df['genres'].apply(parse_genres)
    
    return merged_df

df = load_data()

if df.empty:
    st.stop()

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
             return "https://placehold.co/500x750/1a1a1a/FFF?text=No+Poster"
    except Exception as e:
        return "https://placehold.co/500x750/1a1a1a/FFF?text=Error"

def get_trending_movies(df, n=5):
    if 'popularity' in df.columns:
        return df.sort_values(by='popularity', ascending=False).head(n)
    return df.head(n)

with st.sidebar:
    st.markdown("## <i class='fas fa-film'></i> Cinematch Pro", unsafe_allow_html=True)
    
    total_movies = len(df)
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{total_movies}</div>
        <div class="metric-label">
            <i class="fas fa-film"></i> Total Movies Available
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### <i class='fas fa-search'></i> Filter", unsafe_allow_html=True)
    all_genres = sorted(list(set([g for sublist in df['genre_list'] for g in sublist])))
    selected_genres = st.multiselect("Genre", all_genres)
    
    if selected_genres:
        filtered_movies = df[df['genre_list'].apply(lambda x: any(g in x for g in selected_genres))]
    else:
        filtered_movies = df
        
    st.caption(f"Showing {len(filtered_movies)} movies")
    
    if not df.empty:
        st.markdown("### <i class='fas fa-chart-bar'></i> Genre Distribution", unsafe_allow_html=True)
        genre_counts = pd.Series([g for sublist in filtered_movies['genre_list'] for g in sublist]).value_counts().head(5)
        st.bar_chart(genre_counts, color="#E50914") 
        
    st.markdown("---")
    st.markdown("Developed by Amine.")

if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = ""
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False

st.markdown('<div class="title-text">Unlimited Movies, TV Shows, and More.</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Your personal AI streaming assistant.</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    selected_movie_name = st.selectbox(
        "Search for a movie:",
        filtered_movies['title'].values,
        index=None,
        placeholder="Type to search...",
        label_visibility="collapsed"
    )
    
    if st.button("Get Recommendations", type="primary"): 
        if selected_movie_name:
            st.session_state.selected_movie = selected_movie_name
            st.session_state.show_recommendations = True
            with st.spinner("Crunching data..."):
                st.session_state.recommendations = recommend(selected_movie_name)
        else:
            st.warning("Please select a movie first.")

st.markdown("---")

if st.session_state.show_recommendations and st.session_state.recommendations:
    section_title = f"<i class='fas fa-magic'></i> Best Matches for *{st.session_state.selected_movie}*"
    display_movies = st.session_state.recommendations
else:
    section_title = "<i class='fas fa-chart-line'></i> Trending Now"
    trending_df = get_trending_movies(filtered_movies, n=10)
    display_movies = trending_df['title'].tolist()

st.markdown(f"### {section_title}", unsafe_allow_html=True)


cols = st.columns(5) 

for i, movie_title in enumerate(display_movies):

    movie_row = df[df['title'] == movie_title]
    
    if not movie_row.empty:
        info = movie_row.iloc[0]
        movie_id = info['movie_id']
        overview = info['overview'] if pd.notna(info['overview']) else "No overview available."
        rating = f"{info['vote_average']:.1f}/10" if pd.notna(info['vote_average']) else "N/A"
        date = info['release_date'].split("-")[0] if pd.notna(info['release_date']) else "Unknown"
        poster_url = fetch_poster(movie_id)
    else:
        movie_id = 0
        overview = "Details unavailable."
        rating = "N/A"
        date = "Unknown"
        poster_url = "https://placehold.co/500x750/333/FFF?text=" + movie_title.replace(" ", "+")

    with cols[i % 5]:
        st.markdown(f"""
        <div class="movie-card-container">
            <img src="{poster_url}" class="movie-poster">
            <div class="movie-overlay">
                <div class="overlay-title">{movie_title}</div>
                <div class="overlay-info"><i class="fas fa-calendar-alt"></i> {date}</div>
                <div class="overlay-info"><i class="fas fa-star"></i> {rating}</div>
                <div class="overlay-info" style="font-size: 0.7rem; margin-top: 10px;">{overview[:80]}...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<center style='color: #444; font-size: 0.8rem;'>© 2026 MovieFlix AI. Powered by TMDB API & Streamlit.</center>", unsafe_allow_html=True)
