import logging

from async_signals import Signal

from models import User

# Create a signal
post_save = Signal()


# Connect a function to the signal (can be async or sync, needs to receive **kwargs)
async def create_profile(sender: User, **kwargs):
	logging.critical("Signal received!")
	logging.critical(f"creating a profile for user {sender.email}")

post_save.connect(create_profile)

# Send the signal

