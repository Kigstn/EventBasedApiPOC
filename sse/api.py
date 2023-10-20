import asyncio

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from sse_starlette import EventSourceResponse

from sse._sse_impl import CustomEventSourceResponse


app = FastAPI()


"""
Upsides:
    - enables sending events to the client whenever we want
    - the api stays the same as it is, just has an additional endpoint
        - streaming responses still possible via the normal routes
    - api stays RESTful, sse is basically just a streaming endpoint you never close

Downsides:
    - no streaming responses for the sse connection, do we need that?
    - scaling sse may is difficult (does not really apply to us since we do not have millions of active users)
    - may be annoying if sse connection gets closed / disconnected / renewed while working on answer. Not sure if this really is an issue, but it may be
    - no bilateral communication. Can just send msg from server to client. Currently the client->sever is not needed tho
"""

sse_cache = {}


# initialise the permanent SSE connection and create an event handler
@app.get("/sse")
async def message_stream(request: Request):
    sse_stream = CustomEventSourceResponse(request=request, ping=3)

    # save the stream for lookups
    # logic is just a dummy here, would probly be done by azure id + user ip or sth
    sse_cache["user_name"] = sse_stream

    return sse_stream


@app.post("/msg")
async def message(m: str) -> str:
    # create a task which returns some info to the sse connection
    asyncio.create_task(long_func(user="user_name", m=m))

    return f"Waiting 5s..."


# long running function
async def long_func(user: str, m: str):
    print("Doing stuff for 5s")
    await asyncio.sleep(5)

    # get the user
    user_sse = sse_cache[user]
    await user_sse.send({"xxx": f"Message text was: {m}"})
