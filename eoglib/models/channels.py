from dataclasses import dataclass
from enum import IntEnum

from numpy import array


class ChannelCategory(IntEnum):
    Unknown = 0
    Time = 1
    Position = 2
    Velocity = 3 
    Acceleration = 4
    Jerk = 5
    Stimulus = 6


class ChannelOrientation(IntEnum):
    Unknown = 0
    Horizontal = 1
    Vertical = 2
    Both = 3


class ChannelSource(IntEnum):
    Unknown = 0
    Recorded = 1
    Reference = 2
    Both = 3


@dataclass
class Channel:
    data: array = None
    step: float = None

    @property
    def length(self):
        return (len(self.data) - 1) * self.step

