from typing import Optional

from ..wire import (
    BusMember,
    Net,
    NetState,
    NetChangeCallback,
    BusValueCallback,
)
from ._interface import ReadWriteMemory
from ..undefined import UndefinedBehavior
from ..events import EventScheduler, Timestamp


class RAM62256LP12(ReadWriteMemory):
    """A 62256LP12 SRAM chip."""

    MAX_TIME_ADDR_SET_TO_DATA_OUT_NS = 120
    """Max time for address change to propagate to output."""
    MAX_TIME_SELECTED_TO_DATA_OUT_NS = 120
    """Max time for chip select to propagate to output."""
    MAX_TIME_OUT_ENABLED_TO_DATA_OUT_NS = 60
    """Max time for out enabled to propagate to output."""
    MAX_TIME_END_READ_TO_DATA_HIGHZ_NS = 40
    """Max time from end of read to floating outputs."""

    MAX_TIME_OUT_DISABLED_TO_DATA_HIGHZ_NS = 40
    """Max time from out disabled to floating outputs."""
    MIN_TIME_SELECTED_TO_END_WRITE_NS = 85
    """Min time from chip select to end of write (/WE high)."""
    MIN_TIME_ADDR_SET_TO_END_WRITE_NS = 85
    """Min time from address set to end of write (/WE high)."""
    MIN_TIME_DATA_TO_END_WRITE_NS = 50
    """Min time from data set to end of write (/WE high)."""
    MIN_TIME_WRITE_PULSE_NS = 70
    """Min duration of /WE low pulse during write."""

    def __init__(
        self,
        sched: EventScheduler,
        addr: BusMember,
        data: BusMember,
        chip_select_inv: Net,
        output_enable_inv: Net,
        write_enable_inv: Net,
        image: Optional[dict[int, int]] = None,
    ):
        """
        Initialize the chip.

        :param sched: The event scheduler.
        :param addr: The address bus member to use.
        :param data: The data bus member to use.
        :param chip_select_inv: The active low chip select net.
        :param output_enable_inv: The active low output enable net.
        :param write_enable_inv: The active low write enable net.
        :param image: An optional starting memory image.
        """
        self._sched = sched

        self._addr = addr
        self._data = data
        self._cs_inv = chip_select_inv
        self._oe_inv = output_enable_inv
        self._we_inv = write_enable_inv

        self._cs_stamp = Timestamp()
        self._oe_stamp = Timestamp()
        self._we_stamp = Timestamp()
        self._addr_stamp = Timestamp()
        self._data_stamp = Timestamp()

        self._cs_inv.add_listener(NetChangeCallback(self._cs_inv_did_change))
        self._oe_inv.add_listener(NetChangeCallback(self._oe_inv_did_change))
        self._we_inv.add_listener(NetChangeCallback(self._we_inv_did_change))
        self._data.add_listener(BusValueCallback(self._data_did_change))
        self._addr.add_listener(BusValueCallback(self._addr_did_change))

        self._memory = image or {}

    def peek(self, addr: int) -> int:  # noqa:D102
        return self._memory.get(addr, 0)

    def poke(self, addr: int, value: int):  # noqa:D102
        self._memory[addr] = value

    def _put_output_data_if_ready(self):
        """Put memory data on the bus if ready."""
        if self._oe_inv.state == NetState.LOW and self._cs_inv.state == NetState.LOW:
            output_ready = True
            if (self._sched.now - self._addr_stamp) < Timestamp(
                nanoseconds=self.MAX_TIME_ADDR_SET_TO_DATA_OUT_NS
            ):
                output_ready = False
            elif (self._sched.now - self._oe_stamp) < Timestamp(
                nanoseconds=self.MAX_TIME_OUT_ENABLED_TO_DATA_OUT_NS
            ):
                output_ready = False
            elif (self._sched.now - self._cs_stamp) < Timestamp(
                nanoseconds=self.MAX_TIME_SELECTED_TO_DATA_OUT_NS
            ):
                output_ready = False
            if output_ready:
                self._data.write(self._memory.get(self._addr.value, 0))

    def _cs_inv_did_change(self, value: NetState):
        """
        Handle chip select changes.

        If chip select goes low, submit an event to possibly
        put data on the bus after the worst case delay.

        :param value: The new chip select value.
        """
        self._cs_stamp = self._sched.now
        # Schedule a possible data output
        if value == NetState.LOW:
            self._sched.submit(
                self._sched.now
                + Timestamp(nanoseconds=self.MAX_TIME_SELECTED_TO_DATA_OUT_NS),
                lambda _: self._put_output_data_if_ready(),
            )

    def _oe_inv_did_change(self, value: NetState):
        """
        Handle output enable changes.

        If value goes high, submit an event to float the
        data bus after the worst case delay.

        If value goes low, submit an event to possibly put
        data on the bus after the worst case delay.

        :param value: The new output enable value.
        """
        self._oe_stamp = self._sched.now
        if value == NetState.HIGH:
            # Output disabled. Float the data in the future.
            self._sched.submit(
                self._sched.now
                + Timestamp(nanoseconds=self.MAX_TIME_OUT_DISABLED_TO_DATA_HIGHZ_NS),
                lambda _: self._data.float_(),
            )
        else:
            # Output enabled. Update the output in the future.
            # TODO: What if /WE is low? Raise error?
            self._sched.submit(
                self._sched.now
                + Timestamp(nanoseconds=self.MAX_TIME_OUT_ENABLED_TO_DATA_OUT_NS),
                lambda _: self._put_output_data_if_ready(),
            )

    def _we_inv_did_change(self, value: NetState):
        """
        Handle write enable changes.

        If write enable is now high, chip select is low,
        and output enable is high, check for end of valid write cycle.

        If write enable

        :param value: The new write enable value.
        """
        if (
            value == NetState.HIGH
            and self._cs_inv.state == NetState.LOW
            and self._oe_inv.state == NetState.HIGH
        ):
            # CS = L, OE = H, WE = H
            # Finished possible write pulse, so check the timings
            chip_select_low_time = self._sched.now - self._cs_stamp
            write_enable_low_time = self._sched.now - self._we_stamp
            addr_stable_time = self._sched.now - self._addr_stamp
            data_overlap_time = self._sched.now - self._data_stamp
            if chip_select_low_time < Timestamp(
                nanoseconds=self.MIN_TIME_SELECTED_TO_END_WRITE_NS
            ):
                raise UndefinedBehavior(
                    "Attempted write with insufficient /CS low time"
                )
            if write_enable_low_time < Timestamp(
                nanoseconds=self.MIN_TIME_WRITE_PULSE_NS
            ):
                raise UndefinedBehavior(
                    "Attempted write with insufficient /WE low time"
                )
            if addr_stable_time < Timestamp(
                nanoseconds=self.MIN_TIME_ADDR_SET_TO_END_WRITE_NS
            ):
                raise UndefinedBehavior(
                    "Attempted write with insufficient addr stable time"
                )
            if data_overlap_time < Timestamp(
                nanoseconds=self.MIN_TIME_DATA_TO_END_WRITE_NS
            ):
                raise UndefinedBehavior(
                    "Attempted write with insufficient data stable time"
                )

            # Valid write
            self._memory[self._addr.value] = self._data.value
        elif self._cs_inv.state == NetState.HIGH:
            # CS = H, OE = X, WE = X
            # Do nothing if chip select is high
            pass
        elif value == NetState.LOW and self._oe_inv.state == NetState.LOW:
            # CS = L, OE = L, WE = X
            # We only support WE clocked writes, so if we try to write
            # when OE is low, raise an exception
            raise UndefinedBehavior("Writes with /OE low are not supported!")
        else:
            # CS = L, OE = H, WE = L
            # Start of legal write
            pass

        self._we_stamp = self._sched.now

    def _addr_did_change(self, _):
        """
        Handle changes to the address bus inputs.

        Submit an event to possibly put data on the bus
        after the worst case delay.
        """
        self._addr_stamp = self._sched.now
        # Schedule a possible data output
        self._sched.submit(
            self._sched.now + Timestamp(0, self.MAX_TIME_ADDR_SET_TO_DATA_OUT_NS),
            lambda _: self._put_output_data_if_ready(),
        )

    def _data_did_change(self, _):
        """Handle changes to the data inputs."""
        self._data_stamp = self._sched.now
