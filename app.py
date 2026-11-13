# app.py
import streamlit as st
from backend import generate_answer

st.set_page_config(page_title="Medical Chatbot", page_icon="🩺")

st.title("🩺 Medical Chatbot")
st.caption("AI-powered medical assistant")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_query = st.chat_input("Ask a medical question...")

if user_query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = generate_answer(user_query)
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})