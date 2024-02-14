import abc
from typing import Optional

from ..wire import Pin, Port


class ReadableMemory(metaclass=abc.ABCMeta):
    def __init__(
        self, addr: Port, data: Port, output_enable_inv: Pin, image: dict[int, int]
    ): ...


class ReadWriteMemory(ReadableMemory):
    def __init__(
        self,
        addr: Port,
        data: Port,
        output_enable_inv: Pin,
        write_enable_inv: Pin,
        image: Optional[dict[int, int]] = None,
    ): ...
