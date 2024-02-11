from .pin import Pin
from .pin_state import PinState


class Port:
    def __init__(self, pins: list[Pin]):
        self._pins = pins

    def write(self, value: int):
        for i, p in enumerate(self._pins):
            bit = (value & (1 << i)) >> i
            p.write(PinState.HIGH if bit == 1 else PinState.LOW)

    @property
    def value(self) -> int:
        out = 0
        for i, p in enumerate(self._pins):
            print(i, p.state)
            if p.state == PinState.HIGH:
                out += 1 << i
        return out

    def float_(self):
        for p in self._pins:
            p.write(PinState.FLOATING)
