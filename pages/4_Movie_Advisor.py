import streamlit as st
import requests
import google.generativeai as genai

st.set_page_config(page_title="Movie Advisor", page_icon="🎬")

# ---------- Secrets ----------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# ---------- Gemini Setup ----------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3-flash-preview")

# ---------- TMDb Helpers ----------
def search_movies(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "include_adult": "false",
        "language": "en-US",
        "page": 1
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error(f"Movie search failed: {response.status_code}")
        st.write(response.text)
        return []

    data = response.json()
    return data.get("results", [])

def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {}

    data = response.json()
    genres = data.get("genres", [])
    return {genre["id"]: genre["name"] for genre in genres}

def build_poster_url(poster_path):
    if not poster_path:
        return None
    return f"https://image.tmdb.org/t/p/w500{poster_path}"

# ---------- Page Title ----------
st.title("🎬 Movie Advisor")
st.write("Choose a movie and chat with an AI that knows its API data.")

# ---------- Session State ----------
if "movie_chat_messages" not in st.session_state:
    st.session_state.movie_chat_messages = []

if "selected_movie_context" not in st.session_state:
    st.session_state.selected_movie_context = ""

if "selected_movie_title" not in st.session_state:
    st.session_state.selected_movie_title = ""

# ---------- Movie Input ----------
movie_query = st.text_input("Enter a movie title to load into the chatbot:")

if st.button("Load Movie"):
    if movie_query.strip() == "":
        st.warning("Please enter a movie title.")
    else:
        results = search_movies(movie_query)

        if not results:
            st.error("No movie found.")
        else:
            movie = results[0]
            genre_map = get_genres()

            title = movie.get("title", "Unknown")
            overview = movie.get("overview", "No overview available.")
            release_date = movie.get("release_date", "N/A")
            rating = movie.get("vote_average", "N/A")
            popularity = movie.get("popularity", "N/A")
            poster_url = build_poster_url(movie.get("poster_path"))

            genre_names = []
            for gid in movie.get("genre_ids", []):
                if gid in genre_map:
                    genre_names.append(genre_map[gid])

            genre_text = ", ".join(genre_names) if genre_names else "Unknown"

            movie_context = f"""
Title: {title}
Overview: {overview}
Release Date: {release_date}
Rating: {rating}
Popularity: {popularity}
Genres: {genre_text}
"""

            st.session_state.selected_movie_context = movie_context
            st.session_state.selected_movie_title = title
            st.session_state.movie_chat_messages = [
                {
                    "role": "assistant",
                    "content": f"I’m ready to answer questions about {title}. Ask me anything about the movie."
                }
            ]

            st.success(f"Loaded movie: {title}")

            st.subheader(title)
            st.write(f"**Release Date:** {release_date}")
            st.write(f"**Rating:** {rating}")
            st.write(f"**Popularity:** {popularity}")
            st.write(f"**Genres:** {genre_text}")
            st.write(f"**Overview:** {overview}")

            if poster_url:
                st.image(poster_url, width=250)

# ---------- Show Selected Movie Info ----------
if st.session_state.selected_movie_title != "":
    st.markdown(f"### Current Movie: {st.session_state.selected_movie_title}")

# ---------- Display Chat ----------
for msg in st.session_state.movie_chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
st.markdown("### Suggested Questions")

col1, col2, col3 = st.columns(3)

if col1.button("Spoiler-free summary"):
    st.session_state.movie_chat_messages.append(
        {"role": "user", "content": "Give me a spoiler-free summary of this movie."}
    )
    st.rerun()

if col2.button("Family-friendly?"):
    st.session_state.movie_chat_messages.append(
        {"role": "user", "content": "Is this movie family-friendly?"}
    )
    st.rerun()

if col3.button("Genre and mood"):
    st.session_state.movie_chat_messages.append(
        {"role": "user", "content": "What genre and mood does this movie fit best?"}
    )
    st.rerun()
# ---------- Chat Input ----------
if st.session_state.selected_movie_context != "":
    user_input = st.chat_input("Ask about this movie...")

    if user_input:
        st.session_state.movie_chat_messages.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.write(user_input)

        conversation_text = ""
        for msg in st.session_state.movie_chat_messages:
            role_name = "User" if msg["role"] == "user" else "Assistant"
            conversation_text += f"{role_name}: {msg['content']}\n"

        prompt = f"""
You are a movie advisor chatbot.

You must answer using the movie data below and the ongoing conversation.
Be helpful, clear, and conversational.
You can explain the movie, summarize it without spoilers, comment on its genre, discuss whether it fits certain moods, and answer follow-up questions.

Movie data:
{st.session_state.selected_movie_context}

Conversation so far:
{conversation_text}

Respond to the user's latest message.
"""

        try:
            response = model.generate_content(prompt)
            bot_reply = response.text.strip()
        except Exception:
            bot_reply = "Sorry, I’m having trouble responding right now. Please try again in a moment."

        st.session_state.movie_chat_messages.append(
            {"role": "assistant", "content": bot_reply}
        )

        with st.chat_message("assistant"):
            st.write(bot_reply)
else:
    st.info("Load a movie first to start chatting.")
