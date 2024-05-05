import logging

from async_signals import Signal

from models import Product, ProductFile
from settings.database import Base

# Create a signal
post_save = Signal()
pre_save = Signal()
pre_delete = Signal()


async def create_profile(sender: Product, created: bool, *args, **kwargs):
	if created:
		logging.critical(f"New Product created: {sender.name}")
	logging.critical("Signal received!")


async def delete_product_file(sender: ProductFile, *args, **kwargs):
	sender.delete_file()
	logging.critical("deleted product file")


post_save.connect(create_profile, Product)
pre_delete.connect(delete_product_file, ProductFile)

# Send the signal
