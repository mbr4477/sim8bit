from .net import Net, NetMember
from .pin_state import PinState


class Pin(NetMember):
    def __init__(self, net: Net):
        self._net = net
        self._state = PinState.FLOATING

    @property
    def state(self) -> PinState:
        return self._net.state

    def write(self, state: PinState):
        self._net.notify_changed(self, state)
        self._state = state

    def __hash__(self) -> int:
        return id(self)
