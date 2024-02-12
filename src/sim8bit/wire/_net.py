import abc

from ._pin_state import PinState
from typing import Callable


class ShortError(RuntimeError):
    pass


class NetMember(metaclass=abc.ABCMeta): ...


class PinStateListener(metaclass=abc.ABCMeta):
    def notify_changed(self, state: PinState): ...


class PinStateCallback(PinStateListener):
    def __init__(self, callback: Callable[[PinState], None]):
        super().__init__()
        self._callback = callback

    def notify_changed(self, state: PinState):
        self._callback(state)


class Net:
    def __init__(self):
        self._members: dict[NetMember, PinState] = {}
        self._state = PinState.FLOATING
        self._listeners: list[PinStateListener] = []

    def add_listener(self, listener: PinStateListener):
        self._listeners.append(listener)

    @property
    def state(self) -> PinState:
        return self._state

    def notify_changed(self, member: NetMember, state: PinState):
        self._members[member] = state

        prev_state = self._state
        states = self._members.values()
        if PinState.HIGH in states and PinState.LOW in states:
            raise ShortError
        elif PinState.HIGH in states:
            self._state = PinState.HIGH
        elif PinState.LOW in states:
            self._state = PinState.LOW
        else:
            self._state = PinState.FLOATING

        if prev_state != self._state:
            for listener in self._listeners:
                listener.notify_changed(self._state)


Bus = list[Net]
