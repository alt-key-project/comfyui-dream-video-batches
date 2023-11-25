# -*- coding: utf-8 -*-

class FrameRate:
    TYPE_NAME = "FRAME_RATE"

    def __init__(self, base: int, divisor: int = 1):
        self._base = base
        self._divisor = max(1, divisor)

    def as_float(self) -> float:
        return float(self._base) / self._divisor

    def rounded_int(self) -> int:
        return round(self.as_float())

    def seconds_to_frames(self, seconds: float) -> int:
        return round(self.as_float() * seconds)

    @property
    def base(self) -> int:
        return self._base

    @property
    def divisor(self) -> int:
        return self._divisor

    def __str__(self):
        return "{:.3f}".format(self.as_float())

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        if isinstance(other, FrameRate):
            return abs(self.as_float() - other.as_float()) < 0.001
        else:
            return False
