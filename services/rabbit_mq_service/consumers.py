import json
from collections import namedtuple
from typing import Protocol

from pika.channel import Channel
import logging

from services.rabbit_mq_service.listeners import UserListener
from services.rabbit_mq_service.payload_schemas import RabbitMQPayload


class Queues:
	AccountQueue = "account_queue"
	InventoryQueue = "inventory_queue"
	ReportQueue = "report_queue"
	ChatQueue = "chat_queue"
	CRMQueue = "crm_queue"


ExchangeType = namedtuple('Exchange', ['name', 'type'])
Exchange = ExchangeType("sales_app", "fanout")


class Consumer(Protocol):
	queue_name = ""

	@classmethod
	def consume(cls, ch: Channel, method, properties, body):
		cls.handle_message(body)
		ch.basic_ack(method.delivery_tag, False)

	@staticmethod
	def handle_message(message):
		print(f" [x] Received {message}")
		return


class InventoryConsumer(Consumer):
	queue_name = Queues.InventoryQueue
	@staticmethod
	def handle_message(message: str):
		payload = json.loads(message)
		try:
			payload = RabbitMQPayload(**payload)
			if payload.data_type == "user":
				UserListener.handle_user_data(payload.action, payload.data)
			return
		except TypeError as e:
			logging.critical(e)
			return



