import logging
import asyncio
from collections import defaultdict
from typing import Callable, Type

class Signal:
    def __init__(self):
        self._handlers = defaultdict(set)

    def connect(self, function: Callable, sender_type: Type):
        """Connect a function to a specific sender type."""
        logging.debug(f"Connecting {function} to {sender_type}")
        self._handlers[sender_type].add(function)

    async def send(self, sender, **kwargs):
        """Send a signal to all connected functions."""
        sender_type = type(sender)
        if sender_type not in self._handlers:
            return
        tasks = [function(sender, **kwargs) for function in self._handlers[sender_type]]
        if tasks:
            await asyncio.gather(*tasks)  # Run all connected functions concurrently

# Signal instances for common events
post_save = Signal()
pre_save = Signal()
pre_delete = Signal()
