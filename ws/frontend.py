import streamlit as st
from websockets.sync.client import connect


st.title("ChatGPT-like clone")


def send(websocket, message):
    websocket.send(message)


def receive(websocket):
    message = websocket.recv()
    print(f"Received: {message}")
    return message


websocket = connect("ws://localhost:8000/ws")
print("Connected to websocket")


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

    # send the message over the ws
    send(websocket, prompt)

    # hacky way because of streamlit
    # normally this would an event, and if a message is received from the ws, a new chat msg would be appended
    # no idea how to do this in streamlit, so this will do as a demo
    r = receive(websocket)
    with st.chat_message("assistant"):
        st.markdown(r)
        st.session_state.messages.append({"role": "assistant", "content": r})

    r = receive(websocket)
    with st.chat_message("assistant"):
        st.markdown(r)
        st.session_state.messages.append({"role": "assistant", "content": r})
