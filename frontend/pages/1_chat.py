import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.title("RAG Agent Chatbot")

user_input = st.text_input("Enter your message:")

if st.button("Send") and user_input.strip():
    payload = {
        "message": user_input,
        # "session_id": None,
        "top_k": 4
    }

    response = requests.post(f"{API_BASE}/chat", json=payload, timeout = 60)
    data = response.json()

    st.subheader("Answer")
    st.write(data["answer"])

    st.subheader("Route")
    st.write(data["route"])

    if data.get("sources"):
        st.subheader("Sources")
        for source in data["sources"]:
            st.write(source)