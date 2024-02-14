import pytest
from sim8bit.wire import Net, Pin, Port, ShortError


def test_port():
    bus = [Net() for _ in range(8)]
    uut_reading = Port([Pin(x) for x in bus])
    uut_writing = Port([Pin(x) for x in bus])

    uut_reading.float_()
    uut_writing.write(42)
    assert uut_reading.value == 42


def test_port_len():
    uut = Port([Pin(Net()) for _ in range(8)])
    assert len(uut) == 8


def test_conflicting_writes_raises_short():
    bus = [Net() for _ in range(8)]
    uut_a = Port([Pin(x) for x in bus])
    uut_b = Port([Pin(x) for x in bus])

    uut_a.write(16)
    with pytest.raises(ShortError):
        uut_b.write(0)