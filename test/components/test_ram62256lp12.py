import pytest
from sim8bit.components.ram62256lp12 import RAM62256LP12
from sim8bit.events import EventScheduler, Timestamp
from sim8bit.error import UndefinedBehavior
from sim8bit.wire import BusMember, Net


@pytest.fixture
def sched() -> EventScheduler:
    return EventScheduler()


@pytest.fixture
def addr_bus() -> list[Net]:
    return [Net() for _ in range(12)]


@pytest.fixture
def data_bus() -> list[Net]:
    return [Net() for _ in range(8)]


@pytest.fixture
def chip_select() -> Net:
    return Net()


@pytest.fixture
def output_enable() -> Net:
    return Net()


@pytest.fixture
def write_enable() -> Net:
    return Net()


@pytest.fixture
def ram_chip(
    sched: EventScheduler,
    addr_bus: list[Net],
    data_bus: list[Net],
    chip_select: Net,
    output_enable: Net,
    write_enable: Net,
) -> RAM62256LP12:
    return RAM62256LP12(
        sched,
        BusMember(addr_bus),
        BusMember(data_bus),
        chip_select,
        output_enable,
        write_enable,
    )


def test_write(
    sched: EventScheduler,
    addr_bus: list[Net],
    data_bus: list[Net],
    chip_select: Net,
    output_enable: Net,
    write_enable: Net,
    ram_chip: RAM62256LP12,
):
    addr = BusMember(addr_bus)
    data = BusMember(data_bus)
    cs_hdl = chip_select.take_high()
    _ = output_enable.take_high()
    we_hdl = write_enable.take_high()

    def setup_addr_and_cs(_):
        addr.write(312)
        chip_select.take_low(cs_hdl)

    def setup_data_and_we(_):
        write_enable.take_low(we_hdl)
        data.write(42)

    def finish_write(_):
        write_enable.take_high(we_hdl)

    sched.submit(Timestamp(0, 0), setup_addr_and_cs)
    sched.submit(Timestamp(0, 80), setup_data_and_we)
    sched.submit(Timestamp(0, 160), finish_write)

    while not sched.empty:
        sched.tick()

    assert ram_chip.peek(312) == 42


def test_write_fails_if_we_pulse_too_short(
    sched: EventScheduler,
    addr_bus: list[Net],
    data_bus: list[Net],
    chip_select: Net,
    output_enable: Net,
    write_enable: Net,
    ram_chip: RAM62256LP12,
):
    addr = BusMember(addr_bus)
    data = BusMember(data_bus)
    cs_hdl = chip_select.take_high()
    _ = output_enable.take_high()
    we_hdl = write_enable.take_high()

    def setup_addr_and_cs(_):
        addr.write(312)
        chip_select.take_low(cs_hdl)

    def setup_data_and_we(_):
        write_enable.take_low(we_hdl)
        data.write(42)

    def finish_write(_):
        write_enable.take_high(we_hdl)

    sched.submit(Timestamp(0, 0), setup_addr_and_cs)
    sched.submit(Timestamp(0, 80), setup_data_and_we)
    sched.submit(Timestamp(0, 90), finish_write)

    with pytest.raises(UndefinedBehavior, match="insufficient /WE low time"):
        while not sched.empty:
            sched.tick()


def test_read(
    sched: EventScheduler,
    addr_bus: list[Net],
    data_bus: list[Net],
    chip_select: Net,
    output_enable: Net,
    write_enable: Net,
    ram_chip: RAM62256LP12,
):
    ram_chip.poke(312, 42)

    addr = BusMember(addr_bus)
    data = BusMember(data_bus)
    cs_hdl = chip_select.take_high()
    oe_hdl = output_enable.take_high()
    _ = write_enable.take_high()

    out = -1

    def setup_addr_and_cs(_):
        addr.write(312)
        chip_select.take_low(cs_hdl)

    def start_read(_):
        output_enable.take_low(oe_hdl)

    def read_data(_):
        nonlocal out
        out = data.value

    def finish_read(_):
        output_enable.take_high(oe_hdl)

    sched.submit(Timestamp(0, 0), setup_addr_and_cs)
    sched.submit(Timestamp(0, 80), start_read)
    sched.submit(Timestamp(0, 160), read_data)
    sched.submit(Timestamp(0, 240), finish_read)

    while not sched.empty:
        sched.tick()

    assert out == 42
