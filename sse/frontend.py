import time
from threading import Thread

import httpx
import streamlit as st
from websockets.sync.client import connect


st.title("ChatGPT-like clone")


def receive(message_queue: list):
    with httpx.stream("GET", "http://127.0.0.1:8000/sse") as response:
        print("Connected to sse")

        for r in response.iter_text():
            print(f"Received: {r}")

            # remove pings
            if "ping" not in r:
                message_queue.append(r)


# run sse in threading. just quick hack to get this working
message_queue = []
thread = Thread(target=receive, args=(message_queue,))
thread.start()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # send the message over the normal api
    r = httpx.post("http://127.0.0.1:8000/msg", params={"m": prompt}).text

    with st.chat_message("assistant"):
        st.markdown(r)
        st.session_state.messages.append({"role": "assistant", "content": r})

    # hacky way because of streamlit
    # normally this would an event, and if a message is received from the ws, a new chat msg would be appended
    # no idea how to do this in streamlit, so this will do as a demo
    while not message_queue:
        time.sleep(0.5)

    r = message_queue.pop()
    with st.chat_message("assistant"):
        st.markdown(r)
        st.session_state.messages.append({"role": "assistant", "content": r})
