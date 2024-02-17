import abc
import enum
import itertools
from typing import Callable


class InvalidHandle(RuntimeError): ...


class HandleNotOwner(RuntimeError): ...


class NetState(enum.Enum):
    LOW = 1
    HIGH = 2
    FLOATING = 3


class NetChangeListener(metaclass=abc.ABCMeta):
    def on_change(self, state: NetState): ...


class NetChangeCallback(NetChangeListener):
    def __init__(self, callback: Callable[[NetState], None]):
        super().__init__()
        self._callback = callback

    def on_change(self, state: NetState):
        self._callback(state)


class Net:
    def __init__(self):
        self._owner = 0
        self._state = NetState.FLOATING
        self._listeners: list[NetChangeListener] = []
        self._handles = itertools.count()
        _ = next(self._handles)

    def add_listener(self, listener: NetChangeListener):
        self._listeners.append(listener)

    @property
    def state(self) -> NetState:
        return self._state

    def _verify_allowed(self, handle: int):
        if handle != self._owner:
            raise HandleNotOwner(
                f"Handle {handle} not allowed to mutate net"
                + f" owned by {self._owner}."
            )

    def take_high(self, handle: int = 0) -> int:
        self._verify_allowed(handle)
        if handle == 0:
            self._owner = next(self._handles)
        self._state = NetState.HIGH
        self._notify_listeners()
        return self._owner

    def take_low(self, handle: int = 0) -> int:
        self._verify_allowed(handle)
        if handle == 0:
            self._owner = next(self._handles)
        self._state = NetState.LOW
        self._notify_listeners()
        return self._owner

    def release_floating(self, handle: int):
        self._verify_allowed(handle)
        self._owner = 0
        self._state = NetState.FLOATING

    def _notify_listeners(self):
        for listener in self._listeners:
            listener.on_change(self._state)


Bus = list[Net]
