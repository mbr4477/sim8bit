import pytest
from sim8bit.memory import ROM
from sim8bit.wire import DisallowedFloatingPin, Net, Pin, PinState, Port


def test_read_uninit_memory_is_zero():
    read_enable = Pin(Net())
    read_enable.write(PinState.HIGH)
    uut = ROM(
        Port([Pin(Net()) for _ in range(16)]),
        Port([Pin(Net()) for _ in range(8)]),
        read_enable.copy(),
        {},
    )
    uut.addr().copy().write(1024)
    assert uut.data().value == 0


def test_read():
    read_enable = Pin(Net())
    read_enable.write(PinState.HIGH)
    uut = ROM(
        Port([Pin(Net()) for _ in range(16)]),
        Port([Pin(Net()) for _ in range(8)]),
        read_enable.copy(),
        {512: 21, 1024: 42},
    )
    addr = uut.addr().copy()
    addr.write(1024)
    assert uut.data().value == 42
    addr.write(512)
    assert uut.data().value == 21


def test_data_goes_floating_after_read_disable():
    read_enable = Pin(Net())
    read_enable.write(PinState.HIGH)
    uut = ROM(
        Port([Pin(Net()) for _ in range(16)]),
        Port([Pin(Net()) for _ in range(8)]),
        read_enable.copy(),
        {},
    )
    read_enable.write(PinState.LOW)
    for p in uut.data():
        assert p.state == PinState.FLOATING


def test_raises_disallowed_floating_pin_if_read_enable_floating():
    read_enable = Pin(Net())
    read_enable.float_()
    with pytest.raises(DisallowedFloatingPin):
        _ = ROM(
            Port([Pin(Net()) for _ in range(16)]),
            Port([Pin(Net()) for _ in range(8)]),
            read_enable.copy(),
            {},
        )
