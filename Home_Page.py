import streamlit as st

st.set_page_config(page_title="ReelMatch", page_icon="🎬")

st.title("🎬 Web Development Lab03-04")
st.header("CS 1301")
st.subheader("Web Development Lab03-04 - Movie Finder, Chatbot & more...")
st.subheader("Malia Radcliffe - Omer Raif Ozoglu")

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left.

The following pages are:

1. **Home Page** – Introduction to our project
2. **Movie Explorer** – A movie finder that uses an external web API
3. **Cine Compass** – A movie-themed AI chatbot powered by Google Gemini
4. **AI Movie Night Plannera** – Search for a movie and ask AI questions about it using TMDB and Gemini
5. **Movie Advisor** – A movie recommendation chatbot powered by Google Gemini
""")
