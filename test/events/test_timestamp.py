from sim8bit.events import Timestamp
import pytest


def test_add():
    assert Timestamp(4, 6) == Timestamp(1, 2) + Timestamp(3, 4)


def test_add_with_carry():
    assert Timestamp(2, 2) == Timestamp(1, 999999999) + Timestamp(0, 3)


def test_sub():
    assert Timestamp(1, 2) == Timestamp(4, 6) - Timestamp(3, 4)


def test_sub_with_carry():
    assert Timestamp(1, 999999999) == Timestamp(2, 2) - Timestamp(0, 3)


def test_gt_same_seconds():
    assert Timestamp(1, 2) > Timestamp(1, 1)


def test_gt_same_nanoseconds():
    assert Timestamp(2, 0) > Timestamp(1, 0)


def test_ge_same_seconds_gt():
    assert Timestamp(2, 3) >= Timestamp(2, 0)


def test_ge_same_nanoseconds_gt():
    assert Timestamp(2, 0) >= Timestamp(1, 0)


def test_ge_eq():
    assert Timestamp(2, 0) >= Timestamp(2, 0)


def test_le_same_seconds_gt():
    assert Timestamp(2, 0) <= Timestamp(2, 3)


def test_le_same_nanoseconds_gt():
    assert Timestamp(1, 0) <= Timestamp(2, 0)


def test_le_eq():
    assert Timestamp(2, 0) <= Timestamp(2, 0)


def test_add_not_implemented():
    with pytest.raises(TypeError):
        _ = Timestamp(2, 0) + 10


def test_sub_not_implemented():
    with pytest.raises(TypeError):
        _ = Timestamp(2, 0) - 10


def test_gt_not_implemented():
    with pytest.raises(TypeError):
        _ = Timestamp(2, 0) > 10


def test_lt_not_implemented():
    with pytest.raises(TypeError):
        _ = Timestamp(2, 0) < 10


def test_ge_not_implemented():
    with pytest.raises(TypeError):
        _ = Timestamp(2, 0) >= 10


def test_le_not_implemented():
    with pytest.raises(TypeError):
        _ = Timestamp(2, 0) <= 10
