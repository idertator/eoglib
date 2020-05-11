from dataclasses import dataclass
from enum import IntEnum


class EventCategory(IntEnum):
    Unknown = 0
    Saccade = 1
    Fixation = 2
    Noise = 3


@dataclass
class Event:
    category: EventCategory = EventCategory.Unknown
    onset: int = None
    offset: int = None


@dataclass
class Saccade(Event):
    category: EventCategory = EventCategory.Saccade

    def __str__(self):
        return f'Saccade({self.onset} → {self.offset})'

    def __repr__(self):
        return f'Saccade({self.onset} → {self.offset})'

