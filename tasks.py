from settings.celery_config import celery


@celery.task
def my_periodic_task():
	print("Periodic task executed")

@celery.task
def just_comment():
	print("I have commented o")