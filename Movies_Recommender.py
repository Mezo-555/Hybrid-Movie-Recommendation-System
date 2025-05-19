import streamlit as st
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import requests
import random


def app():
    # ==========================Fetching Posters through the TMDB API======================================#
    def fetch_poster(movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url)

        if data.status_code == 200:
            movie_data = data.json()
            poster_path = movie_data.get('poster_path', None)  # Use get() to avoid KeyError
        else:
            poster_path = None

        if poster_path is None:
            full_path = "https://image.shutterstock.com/z/stock-vector-unavailable-silver-shiny-emblem-scales-pattern-vector-illustration-detailed-1676250781.jpg"
        else:
            full_path = "https://image.tmdb.org/t/p/w500" + poster_path

        return full_path


    # ========================================Function to recommend movies======================================#
    @st.cache_data(show_spinner=False)
    def recommend(movie, technique):
        movie_name = []
        movie_posters = []
        links = []

        a1 = np.array(content_latent_matrix.loc[movie]).reshape(1, -1)
        a2 = np.array(collaborative_latent_matrix.loc[movie]).reshape(1, -1)

        # Calculating the similarity of this movie with the others in the list
        score1 = cosine_similarity(content_latent_matrix, a1).reshape(-1)
        score2 = cosine_similarity(collaborative_latent_matrix, a2).reshape(-1)

        if technique == 'Content-Based':
            content = sorted(enumerate(score1.tolist()), reverse=True, key=lambda x: x[1])
            for i in content[0:50]:
                movie_id = final.iloc[i[0]].movieId
                links.append("https://www.themoviedb.org/movie/{}".format(movie_id))
                movie_posters.append(fetch_poster(movie_id))
                movie_name.append(final.iloc[i[0]].title)
            return links, movie_name, movie_posters

        elif technique == 'Collaborative-Based':
            collaborative = sorted(enumerate(score2.tolist()), reverse=True, key=lambda x: x[1])
            for i in collaborative[0:50]:
                movie_id = final.iloc[i[0]].movieId
                links.append("https://www.themoviedb.org/movie/{}".format(movie_id))
                movie_posters.append(fetch_poster(movie_id))
                movie_name.append(final.iloc[i[0]].title)
            return links, movie_name, movie_posters

        elif technique == 'Hybrid-Based (Recommended)':
            # an average measure of both content and collaborative
            hybrid = sorted(enumerate(((score1 + score2) / 2.0).tolist()), reverse=True, key=lambda x: x[1])
            for i in hybrid[0:50]:
                movie_id = final.iloc[i[0]].movieId
                links.append("https://www.themoviedb.org/movie/{}".format(movie_id))
                movie_posters.append(fetch_poster(movie_id))
                movie_name.append(final.iloc[i[0]].title)
            return links, movie_name, movie_posters

    # ==============================================Loading Data======================================================#
    final = pickle.load(open('MovieRecommender/Final.pkl', 'rb'))
    content_latent_matrix = pickle.load(open('MovieRecommender/content_latent_matrix.pkl', 'rb'))
    collaborative_latent_matrix = pickle.load(open('MovieRecommender/collaborative_latent_matrix.pkl', 'rb'))
    movie_list = pickle.load(open('MovieRecommender/movie_list.pkl', 'rb'))

    # ===========================================App Layout & Integration==========================================#
    def set_bg():
        """
        A function to unpack an image from url and set as bg.
        Returns
        -------
        The background.
        """
        st.markdown(
            f"""
             <style>
             .css-ocqkz7{{
                 backdrop-filter: blur(2px);
             }} 
             .stApp {{
                 background: url("https://www.megacable.com.mx/images/netflix/background-netflix.png");
                 background-size: cover;
             }} 
             </style>
             """,
            unsafe_allow_html=True
        )

    # ===============================================================================================================#
    set_bg()
    movie_emojis = ["🍿", "🎥", "🎞", "🎬", "📺", "📽"]
    st.title("{}Movie Recommender System".format(random.choice(movie_emojis)))

    selected_movie = st.selectbox(
        "Select a movie from the dropdown below,",
        movie_list,
        index=6396)
    st.sidebar.header("Select the Filtering Method:")
    feat = ['Content-Based', 'Collaborative-Based', 'Hybrid-Based (Recommended)']
    features = st.sidebar.radio('', feat, index=feat.index('Hybrid-Based (Recommended)'))

    # ====================================Recommending 10 Similar Movies=======================================#
    # ====================================Checking & creating the session state================================#
    st.subheader("Top 10 Similar Movies Curated For You...")
    movies_per_page = 10

    # Initialize session state variables
    st.session_state.setdefault('previous_movie', selected_movie)
    st.session_state.setdefault('rounds_i', 0)

    # Reset rounds if the selected movie changes
    if selected_movie != st.session_state['previous_movie']:
        st.session_state['previous_movie'] = selected_movie
        st.session_state['rounds_i'] = 0

    # Fetch recommendations
    links, recommended_movie_names, recommended_movie_posters = recommend(selected_movie, features)

    # Button to load more movies
    if st.button("Get More Movies") and st.session_state['rounds_i'] < len(links):
        st.session_state['rounds_i'] += movies_per_page

    # Paginate the movies
    start, end = st.session_state['rounds_i'], st.session_state['rounds_i'] + movies_per_page
    current_links = links[start:end]
    current_names = recommended_movie_names[start:end]
    current_posters = recommended_movie_posters[start:end]

    # Define columns
    cols = st.columns(5)

    # Display movies in the columns
    for idx, (link, name, poster) in enumerate(zip(current_links, current_names, current_posters)):
        col = cols[idx % 5]  # Cycle through columns
        with col:
            st.write(name if len(name) <= 25 else f"{name[:24]}..")
            st.image(poster)
            with st.expander("Get More Info"):
                st.markdown(f"[{name}]({link})")

    # If no more movies to recommend
    if not current_links:
        st.error("No Movies Left To Recommend.")
        st.success("Select a different movie to see its recommendations :)")
