from dataclasses import dataclass, field
from typing import List, Dict

from .channels import Channel, ChannelCategory, ChannelOrientation, ChannelSource
from .events import Event
from .stimulus import Stimulus


def _channel_key(
    category: ChannelCategory,
    orientation: ChannelOrientation,
    source: ChannelSource
) -> int:
    return category.value | orientation.value << 2 | source.value << 4


@dataclass
class Test:
    calibration: bool = False
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
            return self.channels.get(_channel_key(*key), None)
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
            self.channels[_channel_key(*key)] = value
        elif isinstance(key, int):
            self.events[key] = value
        elif isinstance(key, str):
            self.parameters[key] = value
        else:
            raise IndexError('Index type not supported')

