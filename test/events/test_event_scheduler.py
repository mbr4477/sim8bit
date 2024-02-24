from sim8bit.events import EventScheduler, Timestamp
import unittest.mock as mock


def test_empty():
    uut = EventScheduler()
    assert uut.empty


def test_not_empty():
    uut = EventScheduler()
    uut.submit(mock.Mock(), mock.Mock())
    assert not uut.empty


def test_tick_calls_event_after_submitted():
    handler = mock.Mock()
    stamp = mock.Mock()

    uut = EventScheduler()

    uut.submit(stamp, handler)
    uut.tick()

    handler.assert_called_once_with(stamp)


def test_earlier_events_called_first():
    stamp_first = Timestamp(1, 10)
    handler_first = mock.Mock()
    stamp_second = Timestamp(2, 10)
    handler_second = mock.Mock()

    uut = EventScheduler()
    uut.submit(stamp_second, handler_second)
    uut.submit(stamp_first, handler_first)

    uut.tick()
    handler_first.assert_called_once_with(stamp_first)
    handler_second.assert_not_called()
    handler_first.reset_mock()

    uut.tick()
    handler_first.assert_not_called()
    handler_second.assert_called_once_with(stamp_second)


def test_same_timestamps_first_come_first_served():
    stamp_first = Timestamp(1, 10)
    handler_first = mock.Mock()
    stamp_second = Timestamp(1, 10)
    handler_second = mock.Mock()

    uut = EventScheduler()
    uut.submit(stamp_first, handler_first)
    uut.submit(stamp_second, handler_second)

    uut.tick()
    handler_first.assert_called_once_with(stamp_first)
    handler_second.assert_not_called()
    handler_first.reset_mock()

    uut.tick()
    handler_first.assert_not_called()
    handler_second.assert_called_once_with(stamp_second)
