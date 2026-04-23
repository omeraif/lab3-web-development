import streamlit as st
import requests
from google import genai

### Config

st.set_page_config(page_title="AI Movie Night Planner", page_icon="🎬", layout="wide")

TMDB_BEARER_TOKEN = "TMDB_API_TOKEN"
GEMINI_API_KEY = "GEMINI_API_KEY"

TMDB_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_TOKEN}"
}

###Functions to help

def get_genres():
    """
    Fetch official movie genres from TMDB.
    Returns a list of dictionaries like:
    [{"id": 28, "name": "Action"}, ...]
    """
    url = "https://api.themoviedb.org/3/genre/movie/list"
    response = requests.get(url, headers=TMDB_HEADERS, params={"language": "en"})
    response.raise_for_status()
    data = response.json()
    return data.get("genres", [])


def discover_movies_by_genre(genre_id):
    """
    Fetch movies from TMDB using the discover endpoint and a selected genre.
    """
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "page": 1,
        "with_genres": genre_id,
        "vote_count.gte": 100
    }

    response = requests.get(url, headers=TMDB_HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])


def filter_movies_by_runtime_preference(movie_list, runtime_pref):
    """
    Runtime isn't included in discover results by default,
    so this function uses a rough filter based on popularity results already returned.
    To keep the code simple for class purposes, we'll just slice results differently.
    """
    if runtime_pref == "Shorter":
        return movie_list[:5]
    elif runtime_pref == "Longer":
        return movie_list[5:10] if len(movie_list) >= 10 else movie_list[:5]
    else:
        return movie_list[:8]


def build_movie_context(movie_list):
    """
    Convert the movie data into a short text block for Gemini.
    """
    lines = []

    for movie in movie_list[:8]:
        title = movie.get("title", "Unknown Title")
        overview = movie.get("overview", "No overview available.")
        rating = movie.get("vote_average", "N/A")
        release_date = movie.get("release_date", "Unknown")
        popularity = movie.get("popularity", "N/A")

        lines.append(
            f"Title: {title}\n"
            f"Release Date: {release_date}\n"
            f"Rating: {rating}\n"
            f"Popularity: {popularity}\n"
            f"Overview: {overview}\n"
        )

    return "\n----------------------\n".join(lines)


def get_poster_url(poster_path):
    if not poster_path:
        return None
    return f"https://image.tmdb.org/t/p/w500{poster_path}"


def generate_gemini_recommendation(genre_name, mood, runtime_pref, movie_context):
    """
    Send the API data to Gemini and ask for a specialized response.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are a creative movie night planner.

A user wants a movie recommendation based on:
- Genre: {genre_name}
- Mood: {mood}
- Movie length preference: {runtime_pref}

Below is real movie data from TMDB:
{movie_context}

Please do all of the following:
1. Pick the best movie from this list for the user.
2. Explain why it matches their mood.
3. Mention one or two other good backup choices.
4. Suggest a fun snack pairing.
5. Keep the tone engaging and friendly.
6. Make sure your answer is based only on the movie data provided.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


### Page Title & Introduction

st.title("🎬 AI Movie Night Planner")
st.write(
    "Use TMDB movie data plus Gemini AI to get a personalized movie night recommendation."
)

### Inputs here

with st.container():
    st.subheader("Choose your movie night preferences")

    col1, col2, col3 = st.columns(3)

    try:
        genres = get_genres()
        genre_names = [genre["name"] for genre in genres]
        genre_lookup = {genre["name"]: genre["id"] for genre in genres}
    except Exception:
        genres = []
        genre_names = []
        genre_lookup = {}

    with col1:
        selected_genre = st.selectbox("Choose a genre", genre_names)

    with col2:
        mood = st.selectbox(
            "Choose your mood",
            ["Happy", "Sad", "Excited", "Bored", "Stressed", "Romantic", "Adventurous"]
        )

    with col3:
        runtime_pref = st.selectbox(
            "Choose a movie length vibe",
            ["Any", "Shorter", "Longer"]
        )

generate_button = st.button("Generate My Movie Night Plan")

###Main logic here

if generate_button:
    if not TMDB_BEARER_TOKEN or TMDB_BEARER_TOKEN == "TOKEN":
        st.error("TOKON")
    elif not GEMINI_API_KEY or GEMINI_API_KEY == "KEY":
        st.error("Gemini API key.")
    elif not selected_genre:
        st.error("Please choose a genre.")
    else:
        try:
            genre_id = genre_lookup[selected_genre]
            movies = discover_movies_by_genre(genre_id)

            if not movies:
                st.warning("No movies were found for that genre.")
            else:
                filtered_movies = filter_movies_by_runtime_preference(movies, runtime_pref)
                movie_context = build_movie_context(filtered_movies)

                st.subheader("Movies pulled from TMDB")
                movie_cols = st.columns(4)

                for i, movie in enumerate(filtered_movies[:4]):
                    with movie_cols[i % 4]:
                        poster_url = get_poster_url(movie.get("poster_path"))
                        if poster_url:
                            st.image(poster_url, use_container_width=True)

                        st.markdown(f"**{movie.get('title', 'Unknown Title')}**")
                        st.write(f"⭐ Rating: {movie.get('vote_average', 'N/A')}")
                        st.write(f"📅 Release: {movie.get('release_date', 'Unknown')}")

                st.divider()
                st.subheader("Gemini's Movie Night Recommendation")

                with st.spinner("Generating your movie night plan..."):
                    try:
                        llm_text = generate_gemini_recommendation(
                            selected_genre,
                            mood,
                            runtime_pref,
                            movie_context
                        )
                        st.success("Done!")
                        st.write(llm_text)

                    except Exception as llm_error:
                        st.error("Gemini had a problem generating a response.")
                        st.write("Error details:")
                        st.code(str(llm_error))

        except requests.exceptions.RequestException as api_error:
            st.error("There was a TMDB API error.")
            st.code(str(api_error))

        except Exception as general_error:
            st.error("Something unexpected went wrong.")
            st.code(str(general_error))
