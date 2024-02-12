from __future__ import annotations

from typing import Literal

from ._net import Net, NetMember, PinStateListener
from ._pin_state import PinState


class DisallowedFloatingPin(RuntimeError):
    pass


class Pin(NetMember):
    def __init__(self, net: Net):
        self._net = net
        self.float_()

    def add_listener(self, listener: PinStateListener):
        self._net.add_listener(listener)

    @property
    def state(self) -> PinState:
        return self._net.state

    def write(self, state: Literal[PinState.LOW, PinState.HIGH]):
        self._net.notify_changed(self, state)

    def float_(self):
        self._net.notify_changed(self, PinState.FLOATING)

    def copy(self) -> Pin:
        return Pin(self._net)

    def __hash__(self) -> int:
        return id(self)
