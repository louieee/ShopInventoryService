import json
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.testing.plugin.plugin_base import logging

from repositories.sales import SaleRepository
from schemas.sales import FullOrderListItem, FullSaleListItem
from services.rabbit_mq_service.main import rabbit_mq_service
from services.rabbit_mq_service.payload_schemas import RabbitMQPayload, OrderPayload, SalePayload
from signals.helpers import post_save, pre_delete


async def publish_saved_order(sender: int, *args, **kwargs):
	logging.critical("published")
	created = kwargs.get("created", False)
	db:Optional[Session] = kwargs.pop("db", None)
	user = kwargs.pop("user", None)
	if not db or not user:
		return
	order = await SaleRepository(db=db, user=user).get_order_by_id(sender)
	order = FullOrderListItem.model_validate(order)
	payload = RabbitMQPayload(
		action="create" if created else "update",
		data_type="order",
		data=json.dumps(OrderPayload(
			id = order.id,
			product_id=order.product_id,
			sale_id=order.sale_id,
			quantity=order.quantity,
			delivered=order.delivered,
			total_amount=order.total_price,
			date_delivered=order.date_delivered
		).as_dict()))
	rabbit_mq_service.publish(queues={"report_queue"}, data=payload)

async def publish_deleted_order(sender: int, *args, **kwargs):
	db:Optional[Session] = kwargs.pop("db", None)
	user = kwargs.pop("user", None)
	if not db or not user:
		return
	order = await SaleRepository(db=db, user=user).get_order_by_id(sender)
	order = FullOrderListItem.model_validate(order)
	payload = RabbitMQPayload(
		action="delete",
		data_type="order",
		data=json.dumps(OrderPayload(
			id = order.id,
			product_id=order.product_id,
			sale_id=order.sale_id,
			quantity=order.quantity,
			delivered=order.delivered,
			total_amount=order.total_price,
			date_delivered=order.date_delivered
		).as_dict()))
	rabbit_mq_service.publish(queues={"report_queue"}, data=payload)


async def publish_saved_sale(sender: int, *args, **kwargs):
	created = kwargs.get("created", False)
	db:Optional[Session] = kwargs.pop("db", None)
	user = kwargs.pop("user", None)
	if not db or not user:
		return
	sale = await SaleRepository(db=db, user=user).get_by_id(sender)
	sale = FullSaleListItem.model_validate(sale)
	payload = RabbitMQPayload(
		action="create" if created else "update",
		data_type="sale",
		data=json.dumps(SalePayload(
			id = sale.id,
			paid=sale.paid,
			customer_id=sale.customer_id,
			location=sale.location,
			date_ordered=sale.date_ordered,
			date_paid=sale.date_paid
		).as_dict()))
	rabbit_mq_service.publish(queues={"report_queue"}, data=payload)

async def publish_deleted_sale(sender: int, *args, **kwargs):
	db:Optional[Session] = kwargs.pop("db", None)
	user = kwargs.pop("user", None)
	if not db or not user:
		return
	sale = await SaleRepository(db=db, user=user).get_by_id(sender)
	sale = FullSaleListItem.model_validate(sale)
	payload = RabbitMQPayload(
		action="delete",
		data_type="sale",
		data=json.dumps(SalePayload(
			id=sale.id,
			paid=sale.paid,
			customer_id=sale.customer_id,
			location=sale.location,
			date_ordered=sale.date_ordered,
			date_paid=sale.date_paid
		).as_dict()))
	rabbit_mq_service.publish(queues={"report_queue"}, data=payload)

post_save.connect(publish_saved_order)
pre_delete.connect(publish_deleted_order)
post_save.connect(publish_saved_sale)
pre_delete.connect(publish_deleted_sale)