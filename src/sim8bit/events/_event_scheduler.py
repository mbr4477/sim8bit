import logging

from ._event import Event
from ._event_handler import EventHandler
from ._timestamp import Timestamp

_logger = logging.getLogger(__name__)


class EventScheduler:
    """An event scheduler and loop."""

    def __init__(self):
        """Create the scheduler."""
        self._events: list[Event] = []
        self.now = Timestamp()

    def submit(self, stamp: Timestamp, handler: EventHandler):
        """
        Submit a new event.

        New events are insert such that their timestamp
        is strictly less than all events following them.
        That is, events are ordered by timestamp,
        and events with the same timestamp are processed
        first-come-first-served.

        :param stamp: The timestamp when the event should occur.
        :param handler: The handler to be called to process the event.
        """
        insert_at = -1
        for i, e in enumerate(self._events):
            if stamp < e.stamp:
                insert_at = i
                break

        if insert_at < 0:
            self._events.append(Event(stamp, handler))
        else:
            self._events.insert(insert_at, Event(stamp, handler))

    def tick(self):
        """Process one event."""
        event = self._events.pop(0)
        _logger.debug(
            f"{event.stamp.seconds} sec {event.stamp.nanoseconds}"
            + f" ns -- {event.handler}"
        )
        self.now = event.stamp
        event.handler(event.stamp)

    @property
    def empty(self) -> bool:
        """
        True if the event queue is empty.
        """
        return len(self._events) == 0
