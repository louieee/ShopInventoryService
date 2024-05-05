import asyncio
import json
import logging
from typing import List

import boto3
import websockets
from decouple import config

import settings
from settings.jwt_config import create_access_token


class WebSocketUtil:

	@staticmethod
	async def websocket_client(url, payload):
		async with websockets.connect(url) as websocket:
			await websocket.send(payload)
			await websocket.recv()

	@staticmethod
	def get_or_create_eventloop():
		try:
			return asyncio.get_event_loop()
		except RuntimeError as ex:
			if "There is no current event loop in thread" in str(ex):
				loop = asyncio.new_event_loop()
				asyncio.set_event_loop(loop)
				return asyncio.get_event_loop()

	@staticmethod
	def send_websocket(user, payload):
		try:
			token = create_access_token(user)
			url = f"ws://{config('WEBSOCKET_URL', 'localhost')}:8000/ws/{token}/"
			loop = WebSocketUtil.get_or_create_eventloop()
			loop.run_until_complete(WebSocketUtil.websocket_client(url, payload))
		except Exception as e:
			logging.critical(e)

	@staticmethod
	def send_ws_single_channel(user, channel: str, event: str, data: dict):
		payload = json.dumps(dict(channel=channel, event=event, data=data, sender=user.id))
		WebSocketUtil.send_websocket(user, payload)

	@staticmethod
	def send_ws_multiple_channels(user, channels: List[str], event: str, data: dict):
		payload = json.dumps(
			dict(channels=channels, event=event, data=data, sender=user.id)
		)
		WebSocketUtil.send_websocket(user, payload)


class FileSaver:
	upload_type = "file"

	def __init__(self, upload_type: str):
		self.upload_type = upload_type

	def save(self, folder: str, name: str, content: bytes):
		if self.upload_type == "file":
			return self.__save_media_to_folder(folder, name, content)
		elif self.upload_type == "AWS":
			return self.__save_media_to_aws(folder, name, content)
		raise Exception("This upload type is invalid")


	def delete(self, url):
		if self.upload_type == "file":
			return self.__remove_media_from_folder(url)
		elif self.upload_type == "AWS":
			return self.__remove_media_from_aws(url)
		raise Exception("This upload type is invalid")

	@staticmethod
	def __save_media_to_folder(folder: str, name: str, content: bytes) -> str:
		import os

		folder_path = os.path.join(settings.MEDIA_URL, folder)
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
		full_path = os.path.join(folder_path, name)
		with open(full_path, 'wb') as file:
			file.write(content)
		return full_path

	@staticmethod
	def __remove_media_from_folder(url: str):
		import os
		print("url: ",url)
		if os.path.exists(url):
			os.remove(url)
		return


	@staticmethod
	def __save_media_to_aws(folder: str, name: str, content: bytes):
		import os
		file_path = os.path.join(settings.MEDIA_URL, folder, name)
		s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY
		                  , aws_secret_access_key=settings.AWS_SECRET_KEY)
		s3.put_object(Body=content, Bucket=settings.AWS_S3_BUCKET_NAME, Key=file_path)
		s3_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{file_path}"
		return s3_url

	@staticmethod
	def __remove_media_from_aws(url:str):
		s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY
		                  , aws_secret_access_key=settings.AWS_SECRET_KEY)
		s3.delete_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=url)
		return