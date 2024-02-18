from __future__ import annotations

import dataclasses
import logging
import math
from typing import Any

from typing_extensions import Protocol

_logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Timestamp:
    seconds: int = 0
    nanoseconds: int = 0

    def __add__(self, other: Any) -> Timestamp:
        if not isinstance(other, Timestamp):
            return NotImplemented

        nanosec = self.nanoseconds + other.nanoseconds
        carry_seconds = math.floor(nanosec / 1000000000)
        nanosec = nanosec % 1000000000
        return Timestamp(self.seconds + other.seconds + carry_seconds, nanosec)

    def __sub__(self, other: Any) -> Timestamp:
        if not isinstance(other, Timestamp):
            return NotImplemented

        nanosec = self.nanoseconds - other.nanoseconds
        carry_seconds = math.floor(nanosec / 1000000000)
        nanosec = nanosec % 1000000000
        return Timestamp(self.seconds - other.seconds + carry_seconds, nanosec)

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Timestamp):
            return NotImplemented

        return self.seconds > other.seconds or (
            self.seconds == other.seconds and self.nanoseconds > other.nanoseconds
        )

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Timestamp):
            return NotImplemented

        return self.seconds < other.seconds or (
            self.seconds == other.seconds and self.nanoseconds < other.nanoseconds
        )

    def __ge__(self, other: Any) -> bool:
        return self > other or self == other

    def __le__(self, other: Any) -> bool:
        return self < other or self == other


class EventHandler(Protocol):
    def __call__(self, __stamp: Timestamp) -> Any: ...


@dataclasses.dataclass
class Event:
    stamp: Timestamp
    handler: EventHandler


class EventScheduler:
    def __init__(self):
        self._events: list[Event] = []
        self.now = Timestamp()

    def submit(self, stamp: Timestamp, handler: EventHandler):
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
        event = self._events.pop(0)
        _logger.debug(event)
        self.now = event.stamp
        event.handler(event.stamp)

    @property
    def empty(self) -> bool:
        return len(self._events) == 0
