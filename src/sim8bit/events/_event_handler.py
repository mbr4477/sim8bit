from typing_extensions import Protocol

from ._timestamp import Timestamp


class EventHandler(Protocol):  # pragma: nocover
    """A generic event handler."""

    def __call__(self, __stamp: Timestamp):
        """
        Handle an event.

        :param __stamp: The timestamp of the event.
        """
        ...
