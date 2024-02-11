from sim8bit.net import Net, ShortError
from sim8bit.pin_state import PinState
import unittest.mock as mock

import pytest


def test_net_starts_floating():
    uut = Net()
    assert uut.state == PinState.FLOATING


def test_net_high_if_members_high_or_floating():
    uut = Net()
    uut.notify_changed(mock.Mock(), PinState.HIGH)
    assert uut.state == PinState.HIGH

    uut.notify_changed(mock.Mock(), PinState.FLOATING)
    assert uut.state == PinState.HIGH

    uut.notify_changed(mock.Mock(), PinState.HIGH)
    assert uut.state == PinState.HIGH


def test_net_low_if_members_low_or_floating():
    uut = Net()
    uut.notify_changed(mock.Mock(), PinState.LOW)
    assert uut.state == PinState.LOW

    uut.notify_changed(mock.Mock(), PinState.FLOATING)
    assert uut.state == PinState.LOW

    uut.notify_changed(mock.Mock(), PinState.LOW)
    assert uut.state == PinState.LOW


def test_net_changes_state_when_member_changes_state():
    uut = Net()
    member = mock.Mock()
    uut.notify_changed(member, PinState.LOW)
    assert uut.state == PinState.LOW

    uut.notify_changed(member, PinState.HIGH)
    assert uut.state == PinState.HIGH


def test_net_raises_short_if_set_high_when_member_low():
    uut = Net()
    uut.notify_changed(mock.Mock(), PinState.LOW)
    assert uut.state == PinState.LOW

    with pytest.raises(ShortError):
        uut.notify_changed(mock.Mock(), PinState.HIGH)


def test_net_raises_short_if_set_low_when_member_high():
    uut = Net()
    uut.notify_changed(mock.Mock(), PinState.HIGH)
    assert uut.state == PinState.HIGH

    with pytest.raises(ShortError):
        uut.notify_changed(mock.Mock(), PinState.LOW)
