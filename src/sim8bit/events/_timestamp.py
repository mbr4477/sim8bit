from __future__ import annotations

import dataclasses
import math
from typing import Any


@dataclasses.dataclass
class Timestamp:
    """A timestamp with nanosecond precision."""

    seconds: int = 0
    nanoseconds: int = 0

    def __add__(self, other: Any) -> Timestamp:  # noqa:D105
        if not isinstance(other, Timestamp):
            return NotImplemented

        nanosec = self.nanoseconds + other.nanoseconds
        carry_seconds = math.floor(nanosec / 1000000000)
        nanosec = nanosec % 1000000000
        return Timestamp(self.seconds + other.seconds + carry_seconds, nanosec)

    def __sub__(self, other: Any) -> Timestamp:  # noqa:D105
        if not isinstance(other, Timestamp):
            return NotImplemented

        nanosec = self.nanoseconds - other.nanoseconds
        carry_seconds = math.floor(nanosec / 1000000000)
        nanosec = nanosec % 1000000000
        return Timestamp(self.seconds - other.seconds + carry_seconds, nanosec)

    def __gt__(self, other: Any) -> bool:  # noqa:D105
        if not isinstance(other, Timestamp):
            return NotImplemented

        return self.seconds > other.seconds or (
            self.seconds == other.seconds and self.nanoseconds > other.nanoseconds
        )

    def __lt__(self, other: Any) -> bool:  # noqa:D105
        if not isinstance(other, Timestamp):
            return NotImplemented

        return self.seconds < other.seconds or (
            self.seconds == other.seconds and self.nanoseconds < other.nanoseconds
        )

    def __ge__(self, other: Any) -> bool:  # noqa:D105
        return self > other or self == other

    def __le__(self, other: Any) -> bool:  # noqa:D105
        return self < other or self == other
