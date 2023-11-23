# celery_config.py

from celery import Celery
from celery.schedules import crontab

import settings

celery = Celery(
	settings.APP_NAME,
	broker=settings.CELERY_BROKER,  # Replace with your Redis URL
	backend=settings.CELERY_BACKEND,
	include=["tasks"]# Replace with your Redis URL
)




@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
	from tasks import my_periodic_task
	sender.add_periodic_task(
		crontab(minute="*"),
		my_periodic_task.s(),
		name="my_periodic_task",
	)
