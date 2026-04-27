import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Movie Explorer", page_icon="🎬")

API_KEY = st.secrets["TMDB_API_KEY"]

def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error(f"Genre request failed: {response.status_code}")
        st.write(response.text)
        return []

    data = response.json()
    return data.get("genres", [])

def search_movies(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": query,
        "include_adult": "false",
        "language": "en-US",
        "page": 1
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error(f"Search request failed: {response.status_code}")
        st.write(response.text)
        return []

    data = response.json()
    return data.get("results", [])

def discover_movies_by_genre(genre_id):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": API_KEY,
        "with_genres": genre_id,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
        "sort_by": "popularity.desc"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error(f"Discover request failed: {response.status_code}")
        st.write(response.text)
        return []

    data = response.json()
    return data.get("results", [])

def build_poster_url(poster_path):
    if not poster_path:
        return None
    return f"https://image.tmdb.org/t/p/w500{poster_path}"

st.title("🎬 Movie Explorer")
st.write("Search for movies and explore ratings, posters, and trends.")

query = st.text_input("Enter a movie title:")

genres = get_genres()
genre_dict = {genre["name"]: genre["id"] for genre in genres}
selected_genre = st.selectbox("Choose a genre:", ["Any"] + list(genre_dict.keys()))

min_rating = st.slider("Minimum rating:", 0.0, 10.0, 3.0, 0.5)

if st.button("Search Movies"):
    if query.strip() == "" and selected_genre == "Any":
        st.warning("Please enter a movie title or choose a genre.")
    else:
        if query.strip() != "":
            movies = search_movies(query)
        elif selected_genre != "Any":
            chosen_genre_id = genre_dict[selected_genre]
            movies = discover_movies_by_genre(chosen_genre_id)
        else:
            movies = []

        if query.strip() != "" and selected_genre != "Any":
            chosen_genre_id = genre_dict[selected_genre]
            movies = [movie for movie in movies if chosen_genre_id in movie.get("genre_ids", [])]

        movies = [movie for movie in movies if movie.get("vote_average", 0) >= min_rating]

        if not movies:
            st.error("No matching movies found.")
        else:
            st.subheader("Matching Movies")

            chart_data = []

            for movie in movies[:5]:
                title = movie.get("title", "Unknown")
                rating = movie.get("vote_average", 0)
                popularity = movie.get("popularity", 0)
                release_date = movie.get("release_date", "N/A")
                poster_url = build_poster_url(movie.get("poster_path"))

                st.markdown(f"### {title}")
                st.write(f"Release Date: {release_date}")
                st.write(f"Rating: {rating}")
                st.write(f"Popularity: {popularity}")

                if poster_url:
                    st.image(poster_url, width=200)

                chart_data.append({
                    "Title": title,
                    "Rating": rating,
                    "Popularity": popularity
                })

            df = pd.DataFrame(chart_data)

            st.subheader("Ratings Chart")
            fig1, ax1 = plt.subplots()
            ax1.barh(df["Title"], df["Rating"])
            ax1.set_xlabel("Rating")
            ax1.set_title("Movie Ratings")
            plt.tight_layout()
            st.pyplot(fig1)

            st.subheader("Popularity Chart")
            fig2, ax2 = plt.subplots()
            ax2.bar(df["Title"], df["Popularity"])
            ax2.set_ylabel("Popularity")
            ax2.set_title("Movie Popularity")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig2)
