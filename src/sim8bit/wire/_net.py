import abc
import enum
import itertools
from typing import Callable


class HandleNotOwner(RuntimeError):
    """An exception for accessing a net by a non-owner."""


class NetState(enum.Enum):
    """Possible net states."""

    LOW = 1
    HIGH = 2
    FLOATING = 3


class NetChangeListener(metaclass=abc.ABCMeta):  # pragma: nocover
    """A net state change listener."""

    def on_change(self, state: NetState):
        """
        Handle a change in net state.

        :param state: The new net state.
        """
        ...


class NetChangeCallback(NetChangeListener):
    """A net state change listener using a callback."""

    def __init__(self, callback: Callable[[NetState], None]):
        """
        Create the callback listener.

        :param callback: The callback.
        """
        super().__init__()
        self._callback = callback

    def on_change(self, state: NetState):
        """
        Trigger the callback.

        :param state: The new net state.
        """
        self._callback(state)


class Net:
    """A net that allows a single active participant."""

    def __init__(self):
        """Create the net."""
        self._owner = 0
        self._state = NetState.FLOATING
        self._listeners: list[NetChangeListener] = []
        self._handles = itertools.count()
        _ = next(self._handles)

    def add_listener(self, listener: NetChangeListener):
        """Add a net state change listener."""
        self._listeners.append(listener)

    @property
    def state(self) -> NetState:
        """
        Get the net state.

        :returns: The net state.
        """
        return self._state

    def _verify_allowed(self, handle: int):
        """
        Verify that the handle is allowed to mutate the net.

        :param handle: The handle.
        :raises HandleNotOwner: if handle is not the owner.
        """
        if handle != self._owner:
            raise HandleNotOwner(
                f"Handle {handle} not allowed to mutate net"
                + f" owned by {self._owner}."
            )

    def take_high(self, handle: int = 0) -> int:
        """
        Try to put the net in a high state.

        :param handle: The access handle.
        :returns: The handle to use for future access by this owner.
        :raises HandleNotOwner: if handle is not the owner.
        """
        self._verify_allowed(handle)
        if handle == 0:
            self._owner = next(self._handles)
        self._state = NetState.HIGH
        self._notify_listeners()
        return self._owner

    def take_low(self, handle: int = 0) -> int:
        """
        Try to put the net in a low state.

        :param handle: The access handle.
        :returns: The handle to use for future access by this owner.
        :raises HandleNotOwner: if handle is not the owner.
        """
        self._verify_allowed(handle)
        if handle == 0:
            self._owner = next(self._handles)
        self._state = NetState.LOW
        self._notify_listeners()
        return self._owner

    def release_floating(self, handle: int):
        """
        Try to put the net in a floating state.
        This only makes sense after the net has
        been taken high or low, so a handle is required.

        :param handle: The access handle.
        :raises HandleNotOwner: if handle is not the owner.
        """
        self._verify_allowed(handle)
        self._owner = 0
        self._state = NetState.FLOATING
        self._notify_listeners()

    def _notify_listeners(self):
        """Notify all the listeners of the net state."""
        for listener in self._listeners:
            listener.on_change(self._state)
