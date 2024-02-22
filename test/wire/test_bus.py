from sim8bit.wire import BusValueCallback, BusHasFloatingNet, BusMember, NetState
import unittest.mock as mock
import pytest


def test_bus_value_callback():
    callback = mock.Mock()
    value = mock.Mock()
    uut = BusValueCallback(callback)
    uut.on_change(value)
    callback.assert_called_once_with(value)


class TestBusMember:
    def test_len(self):
        uut = BusMember([mock.Mock() for _ in range(4)])
        assert len(uut) == 4

    def test_getitem(self):
        bus = [mock.Mock() for _ in range(4)]
        uut = BusMember(bus)
        for i in range(len(bus)):
            assert uut[i] is bus[i]

    def test_value(self):
        bus = [mock.Mock() for _ in range(4)]
        uut = BusMember(bus)

        bus[0].state = NetState.HIGH
        bus[1].state = NetState.LOW
        bus[2].state = NetState.HIGH
        bus[3].state = NetState.LOW

        assert uut.value == 5

    def test_raises_error_if_floating_net(self):
        bus = [mock.Mock() for _ in range(4)]
        uut = BusMember(bus)

        bus[0].state = NetState.HIGH
        bus[1].state = NetState.FLOATING
        bus[2].state = NetState.HIGH
        bus[3].state = NetState.LOW

        with pytest.raises(BusHasFloatingNet):
            _ = uut.value
