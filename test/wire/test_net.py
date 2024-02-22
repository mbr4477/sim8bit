import unittest.mock as mock

import pytest
from sim8bit.wire import HandleNotOwner, Net, NetChangeCallback, NetState


def test_net_change_callback():
    callback = mock.Mock()
    state = mock.Mock()

    uut = NetChangeCallback(callback)
    uut.on_change(state)

    callback.assert_called_once_with(state)


class TestNet:
    def test_starts_floating(self):
        uut = Net()
        assert uut.state == NetState.FLOATING

    def test_take_high_changes_state_to_high(self):
        uut = Net()
        _ = uut.take_high()
        assert uut.state == NetState.HIGH

    def test_take_low_changes_state_to_low(self):
        uut = Net()
        _ = uut.take_low()
        assert uut.state == NetState.LOW

    def test_release_floating_changes_state_to_floating(self):
        uut = Net()
        handle = uut.take_high()
        uut.release_floating(handle)
        assert uut.state == NetState.FLOATING

    def test_first_handle_is_one(self):
        uut = Net()
        handle = uut.take_high()
        assert handle == 1

    def test_owning_handle_can_make_changes(self):
        uut = Net()
        handle = uut.take_high()
        try:
            uut.take_low(handle)
        except HandleNotOwner:
            pytest.fail("Unexpected HandleNotOwner error")

    def test_non_owning_handle_causes_handle_not_owner_error(self):
        uut = Net()
        _ = uut.take_high()
        with pytest.raises(HandleNotOwner):
            uut.take_low(2)

    def test_request_handle_fails_if_owned(self):
        uut = Net()
        _ = uut.take_high()
        with pytest.raises(HandleNotOwner):
            uut.take_low()

    def test_release_floating_allows_new_owner(self):
        uut = Net()
        handle = uut.take_high()
        try:
            uut.release_floating(handle)
            _ = uut.take_low()
        except HandleNotOwner:
            pytest.fail("Unexpected HandleNotOwner error")

    def test_take_high_notifies_all_listeners(self):
        uut = Net()
        listener_a = mock.Mock()
        listener_b = mock.Mock()
        uut.add_listener(listener_a)
        uut.add_listener(listener_b)

        _ = uut.take_high()
        listener_a.on_change.assert_called_once_with(NetState.HIGH)
        listener_b.on_change.assert_called_once_with(NetState.HIGH)

    def test_take_low_notifies_all_listeners(self):
        uut = Net()
        listener_a = mock.Mock()
        listener_b = mock.Mock()
        uut.add_listener(listener_a)
        uut.add_listener(listener_b)

        _ = uut.take_low()
        listener_a.on_change.assert_called_once_with(NetState.LOW)
        listener_b.on_change.assert_called_once_with(NetState.LOW)

    def test_release_floating_notifies_all_listeners(self):
        uut = Net()
        listener_a = mock.Mock()
        listener_b = mock.Mock()
        uut.add_listener(listener_a)
        uut.add_listener(listener_b)

        h = uut.take_high()
        uut.release_floating(h)
        listener_a.on_change.assert_called_with(NetState.FLOATING)
        listener_b.on_change.assert_called_with(NetState.FLOATING)
