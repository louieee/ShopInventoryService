from typing import Tuple, List

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect
from schemas.inventory import Inventory
from settings.jwt_config import get_current_user

router = APIRouter(prefix="/ws", tags=['websocket'])


class Payload(BaseModel):
	channel: str
	sender: int
	event: str
	data: dict


def is_authenticated(scope):
	token = scope['path_params']['token']
	user = get_current_user(token)
	user = Inventory(**user)
	return user_channels(user)


def user_channels(user: Inventory) -> Tuple[List[str], Inventory]:
	channels = ["general", f"user_{user.id}"]
	# if not user.is_admin:
	# 	channels.append("broadcast")
	# if user.is_admin:
	# 	channels.append("admin")
	return channels, user


class ConnectionManager:
	def __init__(self):
		self.users = dict()
		self.channels = dict()

	async def connect(self, websocket: WebSocket):
		channels, user = is_authenticated(websocket.scope)
		self.users[user.id] = websocket
		for channel in channels:
			if channel not in self.channels:
				self.channels[channel] = set()
			self.channels[channel].add(user.id)
		await websocket.accept()

	async def disconnect(self, websocket: WebSocket):
		channels, user = is_authenticated(websocket.scope)
		del self.users[user.id]
		for channel in channels:
			if channel in self.channels:
				self.channels[channel].remove(user.id)

	async def notify(self, websocket: WebSocket):
		data = await websocket.receive_json()
		channel = data['channel']
		if channel not in self.channels:
			await websocket.send_text("Invalid channel")
			return
		for user in self.channels[channel]:
			await self.users[user].send_json(data)


manager = ConnectionManager()


@router.websocket("/{token}/")
async def websocket_endpoint(websocket: WebSocket, token: str):
	await manager.connect(websocket)
	try:
		while True:
			await manager.notify(websocket)
	except WebSocketDisconnect:
		await manager.disconnect(websocket)
