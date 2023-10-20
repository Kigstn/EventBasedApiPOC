import time
from threading import Thread

import httpx
import streamlit as st
import uvicorn
from fastapi import FastAPI
from websockets.sync.client import connect

from wh.api import Subscription


st.title("ChatGPT-like clone")


app = FastAPI()


@app.post("/wh")
def wh(data: Subscription):
    print(f"Received: {data}")
    message_queue.append(data.data)


# run wh / expose api in threading. just quick hack to get this working
# and it does not work, but only due to threads and how they work
# as this should just explain how it would generally work its fine since:
# --> the value is printed from the thread, just passing it to the main thread makes problems
thread = Thread(
    target=uvicorn.run, args=(app,), kwargs={"host": "0.0.0.0", "port": 8502}
)
thread.start()


message_queue = []

# register wh
httpx.post("http://127.0.0.1:8000/wh", params={"url": "http://127.0.0.1:8502/wh"}).text


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

    # doesnt work in this example
    r = message_queue.pop()
    with st.chat_message("assistant"):
        st.markdown(r)
        st.session_state.messages.append({"role": "assistant", "content": r})
