import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()


"""
### Websockets ###

Upsides:
    - enables sending events to the client whenever we want
    - True bidirectional communication with little overhead for each request

Downsides:
    - no streaming responses for anything!!!
    - requires changing the entire api
    - scaling websockets is difficult (does not really apply to us since we do not have millions of active users)
    - may be annoying if ws connection gets closed / disconnected / renewed while working on answer. Not sure if this really is an issue, but it may be
    - makes the api not as intuitive, as all requests are through the same endpoint and just follow a different data scheme
"""


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # receive messages
    while True:
        # get the msg from the websocket
        data = await websocket.receive_text()

        # some logic which routes messages to functions
        ...

        asyncio.create_task(long_func(websocket, data))


# long running function
async def long_func(websocket: WebSocket, message: str):
    await websocket.send_text(f"Waiting 5s...")
    print("Doing stuff for 5s")
    await asyncio.sleep(5)
    await websocket.send_text(f"Message text was: {message}")
