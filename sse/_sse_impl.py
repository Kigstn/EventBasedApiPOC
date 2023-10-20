import asyncio
from typing import Any
from fastapi import Request

from sse_starlette import EventSourceResponse
from sse_starlette.sse import ServerSentEvent, ensure_bytes


class CustomEventSourceResponse(EventSourceResponse):
    request: Request

    def __init__(self, request: Request, *args, **kwargs):
        self.request = request
        super().__init__(content=None, *args, **kwargs)

    async def __call__(self, scope, receive, send) -> None:
        """
        Save the send function so we can access it
        """

        async def safe_send(message):
            async with self._send_lock:
                return await send(message)

        self._send = safe_send

        await super().__call__(scope, receive, send)

    async def stream_response(self, send) -> None:
        """
        Overwrite the default sending function.

        We do not want to pass a generator that returns results, we want to call it ourselves when can can.
        This is why we call
        """

        await self._send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )

        # run a dummy function to not close the connection
        while True:
            if not self.active:
                break
            await asyncio.sleep(1)

    async def send(self, data: dict) -> None:
        """
        Call this when you want to send data to the client.
        """

        _d = ServerSentEvent(data=data)
        chunk = ensure_bytes(_d, self.sep)
        print(f"chunk: {chunk.decode()}")
        await self._send(
            {"type": "http.response.body", "body": chunk, "more_body": True}
        )

    async def end(self) -> None:
        """
        End / Close the connection
        """

        self.active = False
        await self._send(
            {"type": "http.response.body", "body": b"", "more_body": False}
        )
