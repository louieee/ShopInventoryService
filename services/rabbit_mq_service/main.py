from services.rabbit_mq_service.consumers import Exchange, InventoryConsumer
from services.rabbit_mq_service.rabbit_mq import RabbitMQService

rabbit_mq_service = RabbitMQService(
        exchange=Exchange,
        consumers=[
            InventoryConsumer
        ]
    )