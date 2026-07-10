import streamlit as st
import requests

st.title("RAG Agent Chatbot")

with st.form("chat_form", clear_on_submit=True):
    query = st.text_input("Enter your message:")
    send = st.form_submit_button("Send")

if send and query.strip():
    payload = {"message": query}
    response = requests.post("http://localhost:8000/chat", json=payload)

    if response.ok:
        data = response.json()
        st.subheader("Answer")
        st.write(data["answer"])

        st.subheader("Route")
        st.write(data["route"])

        st.subheader("Sources")
        for src in data["sources"]:
            st.json(src)
    else:
        st.error("Failed to get response from backend.")