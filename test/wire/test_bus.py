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

    def test_value_raises_error_if_floating_net(self):
        bus = [mock.Mock() for _ in range(4)]
        uut = BusMember(bus)

        bus[0].state = NetState.HIGH
        bus[1].state = NetState.FLOATING
        bus[2].state = NetState.HIGH
        bus[3].state = NetState.LOW

        with pytest.raises(BusHasFloatingNet):
            _ = uut.value

    def test_write_sets_state_of_all_nets(self):
        bus = [mock.Mock() for _ in range(4)]
        uut = BusMember(bus)

        uut.write(22)

        assert bus[0].take_low.called
        assert bus[1].take_high.called
        assert bus[2].take_high.called
        assert bus[3].take_low.called

    def test_consecutive_writes_reuse_handles(self):
        bus = [mock.Mock() for _ in range(4)]
        uut = BusMember(bus)
        uut.write(15)
        uut.write(0)
        for b in bus:
            b.take_low.assert_called_with(b.take_high.return_value)

    def test_write_raises_value_error_if_negative(self):
        uut = BusMember([mock.Mock()])
        with pytest.raises(ValueError):
            uut.write(-1)

    def test_float(self):
        bus = [mock.Mock() for _ in range(4)]
        uut = BusMember(bus)

        uut.write(22)
        uut.float_()
        for b in bus:
            assert b.release_floating.called

    def test_notifies_all_listeners(self):
        bus = [mock.Mock() for _ in range(4)]
        listeners = [mock.Mock(), mock.Mock()]
        uut = BusMember(bus)

        bus[0].state = NetState.HIGH
        bus[1].state = NetState.LOW
        bus[2].state = NetState.HIGH
        bus[3].state = NetState.LOW

        for x in listeners:
            uut.add_listener(x)

        uut._net_did_change(mock.Mock())

        for x in listeners:
            x.on_change.assert_called_with(5)
