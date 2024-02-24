import unittest.mock as mock

import pytest
from sim8bit.wire import BusMember, BusValueCallback, NetState, Net


def test_bus_value_callback():
    callback = mock.Mock()
    value = mock.Mock()
    uut = BusValueCallback(callback)
    uut.on_change(value)
    callback.assert_called_once_with(value)


class TestBusMember:
    def test_len(self):
        uut = BusMember([Net() for _ in range(4)])
        assert len(uut) == 4

    def test_getitem(self):
        bus = [Net() for _ in range(4)]
        uut = BusMember(bus)
        for i in range(len(bus)):
            assert uut[i] is bus[i]

    def test_value(self):
        bus = [Net() for _ in range(4)]
        uut = BusMember(bus)

        bus[0].take_high()
        bus[1].take_low()
        bus[2].take_high()
        bus[3].take_low()

        assert uut.value == 5

    def test_value_is_floating_if_net_is_floating(self):
        bus = [Net() for _ in range(4)]
        uut = BusMember(bus)

        bus[0].take_high()
        bus[2].take_high()
        bus[3].take_low()

        assert uut.value == NetState.FLOATING

    def test_write_sets_state_of_all_nets(self):
        bus = [Net() for _ in range(4)]
        uut = BusMember(bus)

        uut.write(22)

        assert bus[0].state == NetState.LOW
        assert bus[1].state == NetState.HIGH
        assert bus[2].state == NetState.HIGH
        assert bus[3].state == NetState.LOW

    def test_consecutive_writes_reuse_handles(self):
        bus = [Net() for _ in range(4)]
        uut = BusMember(bus)
        uut.write(15)
        uut.write(0)
        for b in bus:
            assert b.state == NetState.LOW

    def test_write_raises_value_error_if_negative(self):
        uut = BusMember([Net()])
        with pytest.raises(ValueError):
            uut.write(-1)

    def test_float(self):
        bus = [Net() for _ in range(4)]
        uut = BusMember(bus)

        uut.write(22)
        uut.float_()
        for b in bus:
            assert b.state == NetState.FLOATING

    def test_notifies_all_listeners(self):
        bus = [Net() for _ in range(4)]
        listeners = [mock.Mock(), mock.Mock()]
        uut = BusMember(bus)

        for x in listeners:
            uut.add_listener(x)

        uut.write(5)

        for x in listeners:
            x.on_change.assert_called_with(5)
