from __future__ import annotations

from typing import Callable

from ._net import Net, NetChangeCallback, NetState


class BusValueListener:
    def notify_changed(self, value: int): ...


class BusValueCallback(BusValueListener):
    def __init__(self, callback: Callable[[int], None]):
        super().__init__()
        self._callback = callback

    def notify_changed(self, value: int):
        self._callback(value)


class BusMember:
    def __init__(self, nets: list[Net]):
        self._nets = nets
        for x in self._nets:
            x.add_listener(NetChangeCallback(self._net_did_change))
        self._listeners: list[BusValueListener] = []
        self._handles = [0 for _ in self._nets]

    def __len__(self) -> int:
        return len(self._nets)

    def __getitem__(self, idx: int) -> Net:
        return self._nets[idx]

    def add_listener(self, listener: BusValueListener):
        self._listeners.append(listener)

    def _net_did_change(self, _):
        for listener in self._listeners:
            listener.notify_changed(self.value)

    @property
    def value(self) -> int:
        out = 0
        for i, x in enumerate(self._nets):
            if x.state == NetState.HIGH:
                out += 1 << i
        return out

    def write(self, value: int):
        for i, x in enumerate(self._nets):
            bit = (value & (1 << i)) >> i
            if bit == 1:
                self._handles[i] = x.take_high(self._handles[i])
            else:
                self._handles[i] = x.take_low(self._handles[i])

    def float_(self):
        for i, x in enumerate(self._nets):
            x.release_floating(self._handles[i])
            self._handles[i] = 0
