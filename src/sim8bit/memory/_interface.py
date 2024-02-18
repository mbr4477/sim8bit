import abc


class ReadableMemory(metaclass=abc.ABCMeta):  # pragma: nocover
    """Readable memory."""

    def peek(self, addr: int) -> int:
        """
        Peek into a memory location.

        :param addr: The address.
        """
        ...


class ReadWriteMemory(ReadableMemory):  # pragma: nocover
    """Read/writeable memory."""

    def poke(self, addr: int, value: int):
        """
        Set a value at a memory location.

        :param addr: The address.
        :param value: The value.
        """
        ...
