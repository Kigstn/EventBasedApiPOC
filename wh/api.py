import asyncio

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl


app = FastAPI()


"""
Upsides:
    - enables sending events to the client whenever we want
    - no need to keep connection open, easily scalable and we don't have to deal with disconnects
    - streaming responses, if we want those there
    - the api stays the same as it is, just has an additional endpoint
    - api stays RESTful
    
Downsides:
    - tiny bit of overhead since a new connection is made for every message sent
    - client needs to implement and expose an api
        - need to worry about authentication there, otherwise it could be hijacked by a third party
    - no bilateral communication. Can just send msg from server to client. Currently the client->sever is not needed tho

    --> ** Doesn't seem possible to do expose an api from the client side of the frontend, so not viable!!! ** 
"""


wh_cache = {}


class Subscription(BaseModel):
    event_name: str
    data: str


@app.webhooks.post("new-subscription")
def new_subscription(body: Subscription):
    """
    When we have a message for you we'll send you a POST request with this data to the URL that you register in /wh
    """


@app.post("/wh")
def wh(url: HttpUrl):
    # register a webhook for your user
    wh_cache["user_name"] = str(url)


@app.post("/msg")
async def message(m: str) -> str:
    # create a task which returns some info to the wh connection
    asyncio.create_task(long_func(user="user_name", m=m))

    return f"Waiting 5s..."


# long running function
async def long_func(user: str, m: str):
    print("Doing stuff for 5s")
    await asyncio.sleep(5)
    data = Subscription(event_name="test", data=f"Message text was: {m}")

    # get the user
    user_wh = wh_cache[user]
    r = httpx.post(user_wh, json=data.dict())
    print(r)
