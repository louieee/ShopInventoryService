import json
import logging

from models import Product, ProductFile
from schemas.products import ProductDetailResponse
from services.rabbit_mq_service.main import rabbit_mq_service
from services.rabbit_mq_service.payload_schemas import RabbitMQPayload, ProductPayload
from signals.helpers import post_save, pre_delete


async def delete_product_file(sender: ProductFile, *args, **kwargs):
	sender.delete_file()
	logging.critical("deleted product file")

async def publish_saved_product(sender: Product, *args, **kwargs):
	logging.critical("published")
	created = kwargs.get("created", False)
	product = ProductDetailResponse.model_validate(sender)
	payload = RabbitMQPayload(
		action="create" if created else "update",
		data_type="product",
		data=json.dumps(ProductPayload(
			id=product.id,
			name=product.name,
			brand=product.brand.name,
			inventory=product.inventory.name,
			price=product.price,
			quantity=product.quantity,
			description=product.description,
			category=product.category).as_dict()),
	)
	rabbit_mq_service.publish(queues={"report_queue"}, data=payload)

async def publish_deleted_product(sender: Product, *args, **kwargs):
	product = ProductDetailResponse.model_validate(sender)
	payload = RabbitMQPayload(
		action="delete",
		data_type="product",
		data=json.dumps(ProductPayload(
			id=product.id,
			name=product.name,
			brand=product.brand.name,
			inventory=product.inventory.name,
			price=product.price,
			quantity=product.quantity,
			description=product.description,
			category=product.category).as_dict()),
	)
	rabbit_mq_service.publish(queues={"report_queue"}, data=payload)




post_save.connect(publish_saved_product, Product)
pre_delete.connect(publish_deleted_product, Product)
pre_delete.connect(delete_product_file, ProductFile)

# Send the signal
