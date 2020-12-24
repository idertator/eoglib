from enum import Enum


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



