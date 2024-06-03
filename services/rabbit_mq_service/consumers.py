from collections import namedtuple
from typing import Protocol

from pika.channel import Channel


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


class AccountConsumer(Consumer):
	queue_name = Queues.AccountQueue



class ReportConsumer(Consumer):
	queue_name = Queues.ReportQueue



class InventoryConsumer(Consumer):
	queue_name = Queues.InventoryQueue



class ChatConsumer(Consumer):
	queue_name = Queues.ChatQueue

