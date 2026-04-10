import streamlit as st
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyBIHkN2H7Q15dN9jAvzznq0EXdLbSmGcr0"

st.set_page_config(page_title="CineCompass", page_icon="🎬")

st.title("🎬 CineCompass")
st.subheader("Your movie mood and recommendation chatbot")

st.write("""
Talk to CineCompass about movies, genres, moods, and what to watch next.

Examples:
- Recommend a funny movie for tonight
- I liked Interstellar and Inception, what should I watch next?
- Suggest a family-friendly adventure movie
""")

# ---------- Debug: Check Secrets ----------
st.write("Secrets found:", list(st.secrets.keys()))

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success("Gemini API key found.")
except Exception as e:
    st.error(f"Secret read error: {e}")
    st.stop()

# ---------- Gemini Setup ----------
try:
    genai.configure(api_key=api_key)
    st.success("Gemini configured successfully.")
except Exception as e:
    st.error(f"Gemini configure error: {e}")
    st.stop()

# ---------- Model ----------
try:
    model = genai.GenerativeModel("gemini-3-flash-preview")
    st.success("Gemini model loaded successfully.")
except Exception as e:
    st.error(f"Model error: {e}")
    st.stop()

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I’m CineCompass. Tell me what kind of movie mood you're in, and I’ll help you pick something."
        }
    ]

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Chat Controls")

    if st.button("Clear Chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chat cleared! Tell me what kind of movie you're looking for."
            }
        ]
        st.rerun()

    st.markdown("### Quick Prompts")

    if st.button("Funny movie for tonight"):
        st.session_state.messages.append(
            {"role": "user", "content": "Recommend a funny movie for tonight."}
        )
        st.rerun()

    if st.button("Sci-fi recommendation"):
        st.session_state.messages.append(
            {"role": "user", "content": "Recommend a sci-fi movie with a smart story."}
        )
        st.rerun()

    if st.button("Family movie"):
        st.session_state.messages.append(
            {"role": "user", "content": "Suggest a family-friendly movie for the weekend."}
        )
        st.rerun()

# ---------- Display Chat History ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------- User Input ----------
user_input = st.chat_input("Ask CineCompass about movies...")

if user_input:
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Build conversation memory
    conversation_text = ""
    for msg in st.session_state.messages:
        role_name = "User" if msg["role"] == "user" else "Assistant"
        conversation_text += f"{role_name}: {msg['content']}\n"

    prompt = f"""
You are CineCompass, a helpful movie recommendation chatbot.

Rules:
- Stay on the topic of movies, genres, movie moods, and what to watch.
- Be friendly, clear, and concise.
- Use prior conversation to remember the user's preferences.
- If the user asks something unrelated to movies, gently guide them back to movie topics.
- Recommend movies by mood, genre, tone, or viewing situation.
- Ask a short follow-up question when helpful.

Conversation so far:
{conversation_text}

Respond to the user's latest message.
"""

    # Generate response safely
    try:
        response = model.generate_content(prompt)
        bot_reply = response.text.strip()
    except Exception as e:
        bot_reply = f"Sorry, I’m having trouble responding right now. Error: {e}"

    # Save and display assistant reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)
