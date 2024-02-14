from typing import Optional

from ..wire import (
    DisallowedFloatingPin,
    Pin,
    PinState,
    PinStateCallback,
    Port,
    PortValueCallback,
)
from ._rom import ROM
from ..undefined import UndefinedBehavior


class RAM(ROM):
    def __init__(
        self,
        addr: Port,
        data: Port,
        read_enable: Pin,
        write_enable: Pin,
        image: Optional[dict[int, int]] = None,
    ):
        self._we = write_enable
        self._we.float_()
        self._we.add_listener(PinStateCallback(self._write_enable_did_change))
        super().__init__(addr, data, read_enable, image or {})
        self._data.add_listener(PortValueCallback(self._data_did_change))

    def _update(self):
        if self._re.state == PinState.FLOATING:
            raise DisallowedFloatingPin("read_enable floating!")
        elif self._we.state == PinState.FLOATING:
            raise DisallowedFloatingPin("write_enable floating!")
        elif self._re.state == PinState.HIGH and self._we.state == PinState.HIGH:
            raise UndefinedBehavior("read_enable and write_enable both active!")
        elif self._re.state == PinState.HIGH:
            self._data.write((self._memory.get(self._addr.value, 0)))
        elif self._we.state == PinState.HIGH:
            self._memory[self._addr.value] = self._data.value
        else:
            self._data.float_()

    def _write_enable_did_change(self, _):
        self._update()

    def _data_did_change(self, _):
        self._update()
