from enum import Enum
from re import sub


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

    @classmethod
    def snake_names_dict(cls):
        snake_case = lambda s: sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
        return {
            snake_case(channel.name): channel
            for channel in cls
        }
