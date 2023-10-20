import asyncio

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl


app = FastAPI()


"""
### Long Polling ###

Upsides:
    - enables sending events to the client whenever we want
    - streaming responses, if we want those there
    - the api stays the same as it is, just has an additional endpoint
    - api stays RESTful
    
Downsides:
    - ton of overhead as the client needs to do a requests every second or so
        - honestly I just included this to offer all alternatives. Don't want to do this because of this
    - no bilateral communication. Can just send msg from server to client. Currently the client->sever is not needed tho
    - not really server -> client communication. Just saving messages to a queue and then returning them when queried
"""


message_cache = []


@app.get("/lp")
def m_queue():
    # return a message from the queue if there is any
    if message_cache:
        return message_cache.pop()
    raise HTTPException(status_code=400)


@app.post("/msg")
async def message(m: str) -> str:
    # create a task which returns some info to the wh connection
    asyncio.create_task(long_func(m=m))

    return f"Waiting 5s..."


# long running function
async def long_func(m: str):
    print("Doing stuff for 5s")
    await asyncio.sleep(5)
    message_cache.append(f"Message text was: {m}")
