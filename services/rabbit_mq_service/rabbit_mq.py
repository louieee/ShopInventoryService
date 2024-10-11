import json
import logging
import threading
from typing import List

import pika
from pika.adapters.blocking_connection import BlockingConnection

from helpers.decorators import singleton
from services.rabbit_mq_service.consumers import ExchangeType, Consumer
from decouple import config

from services.rabbit_mq_service.payload_schemas import RabbitMQPayload

# Define the connection parameters to connect to RabbitMQ server
connection_params = pika.ConnectionParameters(host=config("RABBIT_MQ_HOST"), port=config("RABBIT_MQ_PORT"),
                                              credentials=pika.PlainCredentials(config("RABBIT_MQ_USERNAME"),
                                                                                config("RABBIT_MQ_PASSWORD")),
                                              heartbeat=60,  # Send heartbeat every 60 seconds
                                              blocked_connection_timeout=300
                                              )


@singleton
class RabbitMQService:

	def __init__(self, exchange: ExchangeType, consumers: List[Consumer]):
		self.consumers = consumers
		self.queues = set([c.queue_name for c in consumers])
		self.exchange = exchange
		self.connection = BlockingConnection(connection_params)
		self.channel = self.connection.channel()
		self.channel.exchange_declare(exchange_type=exchange.type, exchange=exchange.name, passive=True,
		                              durable=True)
		for consumer in consumers:
			self.channel.queue_declare(queue=consumer.queue_name, passive=True)
		print("connected to rabbitmq")

	def publish(self, queues: set[str], data: RabbitMQPayload):
		data = json.dumps(data.__dict__)
		queues = self.queues.intersection(queues)
		for queue in queues:
			self.channel.queue_bind(queue=queue, exchange=self.exchange.name)
		try:
			self.channel.basic_publish(exchange=self.exchange.name,
			                           routing_key='',
			                           body=data,
			                           mandatory=True)
		except Exception as e:
			logging.critical(e, exc_info=True)
			logging.critical("failed to publish")

	def consume(self):
		for consumer in self.consumers:
			self.channel.queue_bind(queue=consumer.queue_name, exchange=self.exchange.name)

			self.channel.basic_consume(queue=consumer.queue_name,
			                           on_message_callback=consumer.consume,
			                           exclusive=False,
			                           auto_ack=False)
		self.channel.start_consuming()

	def consume_in_background(self):
		thread = threading.Thread(target=self.consume)
		thread.daemon = True
		thread.start()
		print("started rabbit mq in background")

	def publish_in_background(self, queues: set[str], data: RabbitMQPayload):
		thread = threading.Thread(target=self.publish, args=(queues, data))
		thread.daemon = True
		thread.start()
		print("started rabbit mq in background")

# channel.s
