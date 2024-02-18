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
    MAX_TIME_ADDR_SET_TO_DATA_OUT_NS = 120
    MAX_TIME_SELECTED_TO_DATA_OUT_NS = 120
    MAX_TIME_OUT_ENABLED_TO_DATA_OUT_NS = 60
    MAX_TIME_END_READ_TO_DATA_HIGHZ_NS = 40

    MAX_TIME_OUT_DISABLED_TO_DATA_HIGHZ_NS = 40
    MIN_TIME_SELECTED_TO_END_WRITE_NS = 85
    MIN_TIME_ADDR_SET_TO_END_WRITE_NS = 85
    MIN_TIME_DATA_TO_END_WRITE_NS = 50
    MIN_TIME_WRITE_PULSE_NS = 70

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

    def peek(self, addr: int) -> int:
        return self._memory.get(addr, 0)

    def poke(self, addr: int, value: int):
        self._memory[addr] = value

    def _put_output_data_if_ready(self):
        if self._oe_inv.state == NetState.LOW and self._cs_inv.state == NetState.LOW:
            output_ready = True
            if (self._sched.now - self._addr_stamp) < Timestamp(
                0, self.MAX_TIME_ADDR_SET_TO_DATA_OUT_NS
            ):
                output_ready = False
            elif (self._sched.now - self._oe_stamp) < Timestamp(
                0, self.MAX_TIME_OUT_ENABLED_TO_DATA_OUT_NS
            ):
                output_ready = False
            elif (self._sched.now - self._cs_stamp) < Timestamp(
                0, self.MAX_TIME_SELECTED_TO_DATA_OUT_NS
            ):
                output_ready = False
            if output_ready:
                self._data.write(self._memory.get(self._addr.value, 0))

    def _cs_inv_did_change(self, value: NetState):
        self._cs_stamp = self._sched.now
        # Schedule a possible data output
        if value == NetState.LOW:
            self._sched.submit(
                self._sched.now + Timestamp(0, self.MAX_TIME_SELECTED_TO_DATA_OUT_NS),
                lambda _: self._put_output_data_if_ready(),
            )

    def _oe_inv_did_change(self, value: NetState):
        self._oe_stamp = self._sched.now
        if value == NetState.HIGH:
            # Output disabled. Float the data in the future.
            self._sched.submit(
                self._sched.now
                + Timestamp(0, self.MAX_TIME_OUT_DISABLED_TO_DATA_HIGHZ_NS),
                lambda _: self._data.float_(),
            )
        else:
            # Output enabled. Update the output in the future.
            # TODO: What if /WE is low? Raise error?
            self._sched.submit(
                self._sched.now
                + Timestamp(0, self.MAX_TIME_OUT_ENABLED_TO_DATA_OUT_NS),
                lambda _: self._put_output_data_if_ready(),
            )

    def _we_inv_did_change(self, value: NetState):
        if (
            value == NetState.HIGH
            and self._cs_inv.state == NetState.LOW
            and self._oe_inv.state == NetState.HIGH
        ):
            # Finished possible write pulse, so check the timings
            chip_select_low_time = self._sched.now - self._cs_stamp
            write_enable_low_time = self._sched.now - self._we_stamp
            addr_stable_time = self._sched.now - self._addr_stamp
            data_overlap_time = self._sched.now - self._data_stamp
            if chip_select_low_time < Timestamp(
                0, self.MIN_TIME_SELECTED_TO_END_WRITE_NS
            ):
                raise UndefinedBehavior(
                    "Attempted write with insufficient /CS low time"
                )
            if write_enable_low_time < Timestamp(0, self.MIN_TIME_WRITE_PULSE_NS):
                raise UndefinedBehavior(
                    "Attempted write with insufficient /WE low time"
                )
            if addr_stable_time < Timestamp(0, self.MIN_TIME_ADDR_SET_TO_END_WRITE_NS):
                raise UndefinedBehavior(
                    "Attempted write with insufficient addr stable time"
                )
            if data_overlap_time < Timestamp(0, self.MIN_TIME_DATA_TO_END_WRITE_NS):
                raise UndefinedBehavior(
                    "Attempted write with insufficient data stable time"
                )

            # Valid write
            self._memory[self._addr.value] = self._data.value
        else:
            # We only support WE clocked writes, so if we try to write
            # when OE is low, raise an exception
            if self._oe_inv.state != NetState.HIGH:
                raise UndefinedBehavior("Writes with /OE low are not supported!")

        self._we_stamp = self._sched.now

    def _addr_did_change(self, _):
        self._addr_stamp = self._sched.now
        # Schedule a possible data output
        self._sched.submit(
            self._sched.now + Timestamp(0, self.MAX_TIME_ADDR_SET_TO_DATA_OUT_NS),
            lambda _: self._put_output_data_if_ready(),
        )

    def _data_did_change(self, _):
        self._data_stamp = self._sched.now
