from __future__ import annotations

from typing import Callable, Sequence, Union, Literal

from ._net import Net, NetChangeCallback, NetState

BusValue = Union[int, Literal[NetState.FLOATING]]


class BusValueListener:  # pragma: nocover
    """A listener for changes in bus value."""

    def on_change(self, value: BusValue):
        """
        Handle a value change.

        :param value: The new bus value.
        """
        ...


class BusValueCallback(BusValueListener):
    """A bus value listener that triggers a callback."""

    def __init__(self, callback: Callable[[BusValue], None]):
        """
        Create the callback listener.

        :param callback: The callback.
        """
        super().__init__()
        self._callback = callback

    def on_change(self, value: BusValue):
        """
        Trigger the callback.

        :param value: The new bus value.
        """
        self._callback(value)


Bus = Sequence[Net]
"""A type alias for a sequence of nets."""


class BusMember:
    """A bus member that can read/write the bus."""

    def __init__(self, nets: Bus):
        """
        Create the bus interface.

        :param nets: The nets that form the bus.
        """
        self._nets = nets
        for x in self._nets:
            x.add_listener(NetChangeCallback(self._net_did_change))
        self._listeners: list[BusValueListener] = []
        self._handles = [0 for _ in self._nets]

    def __len__(self) -> int:
        """Get the number of nets in the bus."""
        return len(self._nets)

    def __getitem__(self, idx: int) -> Net:
        """Get a net from the bus."""
        return self._nets[idx]

    def add_listener(self, listener: BusValueListener):
        """Add a bus value listener."""
        self._listeners.append(listener)

    def _net_did_change(self, _):
        """Handle a change in one of the bus nets."""
        for listener in self._listeners:
            listener.on_change(self.value)

    @property
    def value(self) -> BusValue:
        """
        Calculate the value on the bus from the net states.

        :returns: The unsigned integer value on the bus or FLOATING.
        """
        out = 0
        for i, x in enumerate(self._nets):
            if x.state == NetState.FLOATING:
                out = NetState.FLOATING
                break
            elif x.state == NetState.HIGH:
                out += 1 << i
        return out

    def write(self, value: int):
        """
        Write an unsigned integer value to the bus.

        :raises ValueError: If value is negative.
        """
        if value < 0:
            raise ValueError

        for i, x in enumerate(self._nets):
            bit = (value & (1 << i)) >> i
            if bit == 1:
                self._handles[i] = x.take_high(self._handles[i])
            else:
                self._handles[i] = x.take_low(self._handles[i])

    def float_(self):
        """Put the bus in a floating state."""
        for i, x in enumerate(self._nets):
            x.release_floating(self._handles[i])
            self._handles[i] = 0
