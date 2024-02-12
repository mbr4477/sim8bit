import unittest.mock as mock

from sim8bit.wire import Pin, PinState


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

    uut.write(PinState.HIGH)
    mock_net.notify_changed.assert_called_with(uut, PinState.HIGH)

    uut.write(PinState.LOW)
    mock_net.notify_changed.assert_called_with(uut, PinState.LOW)


def test_float_notifies_net():
    mock_net = mock.Mock()
    uut = Pin(mock_net)
    uut.float_()
    mock_net.notify_changed.assert_called_with(uut, PinState.FLOATING)


def test_copy_returns_new_pin_with_same_net():
    mock_net = mock.Mock()
    uut = Pin(mock_net)
    copied = uut.copy()
    assert copied._net == mock_net
    assert copied is not uut
