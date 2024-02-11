import unittest.mock as mock

from sim8bit.pin import Pin
from sim8bit.pin_state import PinState


def test_pin_starts_floating():
    mock_net = mock.Mock()
    mock_net.state = PinState.HIGH
    uut = Pin(mock_net)
    assert uut.state == PinState.HIGH

    mock_net.state = PinState.LOW
    assert uut.state == PinState.LOW


def test_write_notifies_net():
    mock_net = mock.Mock()
    uut = Pin(mock_net)

    for x in PinState:
        uut.write(x)
        mock_net.notify_changed.assert_called_with(uut, x)
