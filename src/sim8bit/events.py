from __future__ import annotations

import dataclasses
import logging
import math
from typing import Any

from typing_extensions import Protocol

_logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Timestamp:
    """A timestamp with nanosecond precision."""

    seconds: int = 0
    nanoseconds: int = 0

    def __add__(self, other: Any) -> Timestamp:  # noqa:D105
        if not isinstance(other, Timestamp):
            return NotImplemented

        nanosec = self.nanoseconds + other.nanoseconds
        carry_seconds = math.floor(nanosec / 1000000000)
        nanosec = nanosec % 1000000000
        return Timestamp(self.seconds + other.seconds + carry_seconds, nanosec)

    def __sub__(self, other: Any) -> Timestamp:  # noqa:D105
        if not isinstance(other, Timestamp):
            return NotImplemented

        nanosec = self.nanoseconds - other.nanoseconds
        carry_seconds = math.floor(nanosec / 1000000000)
        nanosec = nanosec % 1000000000
        return Timestamp(self.seconds - other.seconds + carry_seconds, nanosec)

    def __gt__(self, other: Any) -> bool:  # noqa:D105
        if not isinstance(other, Timestamp):
            return NotImplemented

        return self.seconds > other.seconds or (
            self.seconds == other.seconds and self.nanoseconds > other.nanoseconds
        )

    def __lt__(self, other: Any) -> bool:  # noqa:D105
        if not isinstance(other, Timestamp):
            return NotImplemented

        return self.seconds < other.seconds or (
            self.seconds == other.seconds and self.nanoseconds < other.nanoseconds
        )

    def __ge__(self, other: Any) -> bool:  # noqa:D105
        return self > other or self == other

    def __le__(self, other: Any) -> bool:  # noqa:D105
        return self < other or self == other


class EventHandler(Protocol):
    """A generic event handler."""

    def __call__(self, __stamp: Timestamp):
        """
        Handle an event.

        :param __stamp: The timestamp of the event.
        """
        ...


@dataclasses.dataclass
class Event:
    """An event with timestamp and handler."""

    stamp: Timestamp
    handler: EventHandler


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
            if stamp.seconds < e.stamp.seconds or (
                stamp.seconds == e.stamp.seconds
                and stamp.nanoseconds < e.stamp.nanoseconds
            ):
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
            + f" ns -- {event.handler.__qualname__}"
        )
        self.now = event.stamp
        event.handler(event.stamp)

    @property
    def empty(self) -> bool:
        """
        True if the event queue is empty.
        """
        return len(self._events) == 0
