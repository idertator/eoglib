from enum import Enum
from re import sub


def _snake_case(name: str) -> str:
    return sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


class Channel(Enum):
    Unknown = 'unknown'
    Timestamps = 'timestamps'
    Time = 'time'
    Stimulus = 'stimulus'
    Horizontal = 'horizontal'
    Vertical = 'vertical'
    Annotations = 'annotations'
    Velocity = 'velocity'
    PositionReference = 'y0'
    VelocityReference = 'v0'

    @property
    def snake_name(self) -> str:
        return _snake_case(self.name)

    @classmethod
    def snake_names_dict(cls):
        return {
            _snake_case(channel.name): channel
            for channel in cls
        }
