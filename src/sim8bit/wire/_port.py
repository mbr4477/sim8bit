from __future__ import annotations

from ._pin import Pin
from ._net import PinStateCallback
from ._pin_state import PinState
from typing import Callable


class PortValueListener:
    def notify_changed(self, value: int): ...


class PortValueCallback(PortValueListener):
    def __init__(self, callback: Callable[[int], None]):
        super().__init__()
        self._callback = callback

    def notify_changed(self, value: int):
        self._callback(value)


class Port:
    def __init__(self, pins: list[Pin]):
        self._pins = pins
        for p in self._pins:
            p.add_listener(PinStateCallback(self._pin_did_change))
        self._listeners: list[PortValueListener] = []

    def __len__(self) -> int:
        return len(self._pins)

    def __getitem__(self, idx: int) -> Pin:
        return self._pins[idx]

    def add_listener(self, listener: PortValueListener):
        self._listeners.append(listener)

    def _pin_did_change(self, _):
        for listener in self._listeners:
            listener.notify_changed(self.value)

    @property
    def value(self) -> int:
        out = 0
        for i, p in enumerate(self._pins):
            if p.state == PinState.HIGH:
                out += 1 << i
        return out

    def write(self, value: int):
        for i, p in enumerate(self._pins):
            bit = (value & (1 << i)) >> i
            p.write(PinState.HIGH if bit == 1 else PinState.LOW)

    def float_(self):
        for p in self._pins:
            p.float_()

    def copy(self) -> Port:
        return Port([p.copy() for p in self._pins])
