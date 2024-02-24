import dataclasses

from ._event_handler import EventHandler
from ._timestamp import Timestamp


@dataclasses.dataclass
class Event:
    """An event with timestamp and handler."""

    stamp: Timestamp
    handler: EventHandler
