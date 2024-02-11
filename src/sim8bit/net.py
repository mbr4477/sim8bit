import abc

from .pin_state import PinState


class ShortError(RuntimeError):
    pass


class NetMember(metaclass=abc.ABCMeta):
    def get_state(self) -> PinState: ...


class Net:
    def __init__(self):
        self._members: dict[NetMember, PinState] = {}
        self._state = PinState.FLOATING

    @property
    def state(self) -> PinState:
        return self._state

    def notify_changed(self, member: NetMember, state: PinState):
        if member not in self._members:
            self._members
        self._members[member] = state
        states = self._members.values()
        if PinState.HIGH in states and PinState.LOW in states:
            raise ShortError
        elif PinState.HIGH in states:
            self._state = PinState.HIGH
        elif PinState.LOW in states:
            self._state = PinState.LOW
        else:
            self._state = PinState.FLOATING
