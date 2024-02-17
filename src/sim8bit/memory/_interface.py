import abc
from typing import Optional

from ..wire import Net, BusMember


class ReadableMemory(metaclass=abc.ABCMeta):
    def __init__(
        self,
        addr: BusMember,
        data: BusMember,
        chip_select_inv: Net,
        output_enable_inv: Net,
        image: dict[int, int],
    ): ...


class ReadWriteMemory(ReadableMemory):
    def __init__(
        self,
        addr: BusMember,
        data: BusMember,
        chip_select_inv: Net,
        output_enable_inv: Net,
        write_enable_inv: Net,
        image: Optional[dict[int, int]] = None,
    ): ...
