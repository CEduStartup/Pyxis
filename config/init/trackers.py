"""Creates and initialize components requred for trackers processing.
"""

from config.mq import queue_host, queue_port, COLLECTOR_TUBE
from shared.events.EventManager import GEventSender
from shared.events.GEventDispatcher import GEventDispatcher

sender = GEventSender()

# Events dispatcher object for collector.
event_dispatcher = GEventDispatcher(queue_host, queue_port, (COLLECTOR_TUBE,))

