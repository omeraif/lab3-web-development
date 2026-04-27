import streamlit as st
from google import genai

st.set_page_config(page_title="CineCompass", page_icon="🎬")

st.title("🎬 CineCompass")
st.subheader("Your movie mood and recommendation chatbot")

st.write("""
Talk to CineCompass about movies, genres, moods, and what to watch next.
""")

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I’m CineCompass. Tell me what kind of movie mood you're in, and I’ll help you pick something."
        }
    ]

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

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask CineCompass about movies...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

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

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        bot_reply = response.text.strip()
    except Exception as e:
        bot_reply = f"Sorry, I’m having trouble responding right now. Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant"):
        st.write(bot_reply)
