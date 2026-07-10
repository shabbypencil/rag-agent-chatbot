import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/chat"

st.title("RAG Agent Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_route" not in st.session_state:
    st.session_state.last_route = None

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

messages_container = st.container()

with messages_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with st.form("chat_form", clear_on_submit=True, enter_to_submit=True):
    query = st.text_input("Enter your message:")
    send = st.form_submit_button("Send")

if send and query.strip():
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("Thinking...", show_time=True):
        response = requests.post(BACKEND_URL, json={"message": query}, timeout=60)
        data = response.json()

    answer = data.get("answer", "No answer returned.")
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.last_route = data.get("route")
    st.session_state.last_sources = data.get("sources", [])

    st.rerun()

if st.session_state.last_route:
    st.subheader("Route")
    st.write(st.session_state.last_route)

if st.session_state.last_sources:
    st.subheader("Sources")
    for src in st.session_state.last_sources:
        st.json(src)