import asyncio
import json
import logging
from typing import List

import websockets
from decouple import config

from settings.jwt_config import create_access_token


async def websocket_client(url, payload):
    async with websockets.connect(url) as websocket:
        await websocket.send(payload)
        await websocket.recv()


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


def send_websocket(user, payload):
    try:
        token = create_access_token(user)
        url = f"ws://{config('WEBSOCKET_URL', 'localhost')}:8000/ws/{token}/"
        loop = get_or_create_eventloop()
        loop.run_until_complete(websocket_client(url, payload))
    except Exception as e:
        logging.critical(e)


def send_ws_single_channel(user, channel: str, event: str, data: dict):
    payload = json.dumps(dict(channel=channel, event=event, data=data, sender=user.id))
    send_websocket(user, payload)


def send_ws_multiple_channels(user, channels: List[str], event: str, data: dict):
    payload = json.dumps(
        dict(channels=channels, event=event, data=data, sender=user.id)
    )
    send_websocket(user, payload)

