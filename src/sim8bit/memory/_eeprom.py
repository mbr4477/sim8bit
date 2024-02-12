import copy

from ..wire import (
    DisallowedFloatingPin,
    Pin,
    PinState,
    PinStateCallback,
    Port,
    PortValueCallback,
)
from ._interface import ReadableMemory


class EEPROM(ReadableMemory):
    def __init__(self, addr: Port, data: Port, read_enable: Pin):
        super().__init__()
        self._memory: dict[int, int] = {}
        self._addr = addr
        self._data = data
        self._re = read_enable
        self._re.float_()
        self._re.add_listener(PinStateCallback(self._read_enable_did_change))
        self._addr.float_()
        self._addr.add_listener(PortValueCallback(self._addr_did_change))

        self._update()

    def _update(self):
        if self._re.state == PinState.FLOATING:
            raise DisallowedFloatingPin
        elif self._re.state == PinState.HIGH:
            self._data.write((self._memory.get(self._addr.value, 0)))
        elif self._re.state == PinState.LOW:
            self._data.float_()

    def _addr_did_change(self, _):
        self._update()

    def _read_enable_did_change(self, _):
        self._update()

    def read_enable(self) -> Pin:
        return self._re

    def addr(self) -> Port:
        return self._addr

    def data(self) -> Port:
        return self._data

    def flash(self, image: dict[int, int]):
        self._memory = copy.copy(image)
