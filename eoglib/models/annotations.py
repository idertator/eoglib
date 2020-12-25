from enum import Enum
from typing import Union


class Event(Enum):
    Unknown = 'unknown'
    Saccade = 'saccade'
    Fixation = 'fixation'
    Noise = 'noise'


class Annotation:

    def __init__(
        self,
        event: Event = Union[str, Event],
        onset: int = -1,
        offset: int = -1
    ):
        if isinstance(event, str):
            event = Event(event)
        assert isinstance(event, Event)
        self._event = event

        assert isinstance(onset, int)
        self._onset = onset

        assert isinstance(offset, int)
        self._offset = offset

        assert onset <= offset

    def __str__(self):
        return f'{self._event.name}({self.onset} → {self.offset})'

    @property
    def event(self) -> Event:
        return self._event

    @event.setter
    def event(self, value: Union[str, Event]):
        if isinstance(value, str):
            value = Event(value)
        assert isinstance(value, Event)
        self._event = value

    @property
    def onset(self) -> int:
        return self._onset

    @onset.setter
    def onset(self, value: int):
        assert isinstance(value, int)
        self._onset = value

    @property
    def offset(self) -> int:
        return self._offset

    @offset.setter
    def offset(self, value: int):
        assert isinstance(value, int)
        self._offset = value

    @classmethod
    def from_json(cls, json: dict):
        return cls(**json)

    def to_json(self) -> dict:
        return {
            'event': self._event,
            'onset': self._onset,
            'offset': self._offset,
        }
