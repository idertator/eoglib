from enum import IntEnum
from dataclasses import dataclass, field
from typing import List, Dict, Type

from numpy import array


class SubjectStatus(IntEnum):
    Unknown = 0
    Healthy = 1
    Presymptomatic = 2
    Sick = 3


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


def ChannelDescriptor(
    category: ChannelCategory,
    orientation: ChannelOrientation,
    source: ChannelSource
) -> int:
    return category.value | orientation.value << 2 | source.value << 4


class EventCategory(IntEnum):
    Unknown = 0
    Saccade = 1
    Fixation = 2
    Noise = 3


class StimulusCategory(IntEnum):
    Unknown = 0
    Saccadic = 1


@dataclass
class Stimulus:
    category: StimulusCategory = StimulusCategory.Unknown


@dataclass
class SaccadicStimulus(Stimulus):
    category: StimulusCategory = StimulusCategory.Saccadic
    angle: int = None


@dataclass
class Event:
    category: EventCategory = EventCategory.Unknown
    onset: int = None
    offset: int = None


@dataclass
class Channel:
    data: array = None
    step: float = None

    @property
    def length(self):
        return (len(self.data) - 1) * self.step


@dataclass
class Test:
    stimulus: Stimulus = None
    events: List[Event] = field(default_factory=list)
    channels: Dict[int, Channel] = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)

    def __len__(self):
        return len(self.events)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            if len(key) != 3:
                raise IndexError('Invalid index channel descriptors')
            return self.channels.get(ChannelDescriptor(*key), None)
        elif isinstance(key, int):
            return self.events[key]
        elif isinstance(key, str):
            return self.parameters[key]
        else:
            raise IndexError('Index type not supported')

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            if len(key) != 3:
                raise IndexError('Invalid index channel descriptors')
            if not isinstance(value, Channel):
                raise TypeError('The value must be of type Channel')
            self.channels[ChannelDescriptor(*key)] = value
        elif isinstance(key, int):
            self.events[key] = value
        elif isinstance(key, str):
            self.parameters[key] = value
        else:
            raise IndexError('Index type not supported')


@dataclass
class Record:
    filename: str = ''
    status: SubjectStatus = SubjectStatus.Unknown
    tests: List[Test] = field(default_factory=list)
    calibration: Dict[ChannelCategory, float] = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)

    def __len__(self):
        return len(self.tests)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.tests[key]
        elif isinstance(key, str):
            return self.parameters[key]
        raise IndexError('Index type is not supported')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if not isinstance(value, Test):
                raise TypeError('The value must be of type Test')
            self.tests[key] = value
        elif isinstance(key, str):
            self.parameters[key] = value
            self.tests[key] = value
        else:
            raise IndexError('Index type is not supported')

    def __add__(self, value):
        if not isinstance(value, Test):
            raise TypeError('The value must be of type Test')
        self.tests.append(value)

