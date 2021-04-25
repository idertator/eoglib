from enum import Enum, IntEnum
from math import floor, ceil
from random import randint
from typing import Union

from numpy import ndarray, int8, zeros, ones, hstack

from .base import Model


class Category(Enum):
    Unknown = 'unknown'
    Saccadic = 'saccadic'


class Orientation(Enum):
    Unknown = 'unknown'
    Horizontal = 'horizontal'
    Vertical = 'vertical'


class Position(IntEnum):
    Unknown = 0
    Left = 1
    Right = 2
    Top = 4
    Bottom = 8
    Center = 16

    @property
    def marker(self) -> str:
        return {
            Position.Unknown: '',
            Position.Left: 'l',
            Position.Right: 'r',
            Position.Top: 't',
            Position.Bottom: 'b',
            Position.Center: 'c',
        }[self]


    @property
    def stimulus(self) -> str:
        return {
            Position.Unknown: 0,
            Position.Left: -1,
            Position.Right: 1,
            Position.Top: 1,
            Position.Bottom: -1,
            Position.Center: 0,
        }[self]


class Stimulus(Model):
    category = Category.Unknown

    def __init__(
        self,
        calibration: bool
    ):
        assert isinstance(calibration, bool)
        self._calibration = calibration

    @property
    def calibration(self) -> str:
        return self._calibration

    @calibration.setter
    def calibration(self,  value: bool):
        assert isinstance(value, bool)
        self._calibration = value

    @classmethod
    def from_json(cls, json: dict):
        json.pop('category')
        return cls(**json)

    def to_json(self) -> dict:
        cls = type(self)
        return {
            'category': cls.category,
            'calibration': self._calibration,
        }


class SaccadicStimulus(Stimulus):
    category = Category.Saccadic

    def __init__(
        self,
        calibration: bool = False,
        angle: int = 0,
        fixation_duration: float = 0.0,
        fixation_variability: float = 0.0,
        saccades_count: int = 0,
        orientation: Union[int, Orientation] = Orientation.Unknown,
        channel: ndarray = None,
        **parameters
    ):
        super(SaccadicStimulus, self).__init__(calibration)

        assert isinstance(angle, int)
        self._angle = angle

        assert isinstance(fixation_duration, float)
        self._fixation_duration = fixation_duration

        assert isinstance(fixation_variability, float)
        self._fixation_variability = fixation_variability

        assert isinstance(saccades_count, int)
        self._saccades_count = saccades_count

        if isinstance(orientation, str):
            orientation = Orientation(orientation)
        assert isinstance(orientation, Orientation)
        self._orientation = orientation

        self._channel = channel

    def __len__(self):
        if self._channel is not None:
            return len(self._channel)
        return 0

    def __getitem__(self, index: int) -> float:
        return self._channel[index]

    def __str__(self):
        angle = f'{self._angle}\u00B0'
        if self._orientation == Orientation.Horizontal:
            if self.calibration:
                return 'Horizontal Calibration {angle}'.format(angle=angle)
            return 'Horizontal Saccadic {angle}'.format(angle=angle)
        if self._orientation == Orientation.Vertical:
            if self.calibration:
                return 'Vertical Calibration {angle}'.format(angle=angle)
            return 'Vertical Saccadic {angle}'.format(angle=angle)
        return 'Unknown Saccadic Test'

    @property
    def angle(self) -> int:
        return self._angle

    @angle.setter
    def angle(self, value: int):
        assert isinstance(value, int)
        self._angle = value

    @property
    def fixation_duration(self) -> float:
        return self._fixation_duration

    @fixation_duration.setter
    def fixation_duration(self, value: float):
        assert isinstance(value, float)
        self._fixation_duration = value

    @property
    def fixation_variability(self) -> float:
        return self._fixation_variability

    @fixation_variability.setter
    def fixation_variability(self, value: float):
        assert isinstance(value, float)
        self._fixation_variability = value

    @property
    def saccades_count(self) -> int:
        return self._saccades_count

    @saccades_count.setter
    def saccades_count(self, value: int):
        assert isinstance(value, int)
        self._saccades_count = value

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    def generate_channel(self, sampling_rate: float) -> ndarray:
        if self._channel is None:
            samples = floor(self.fixation_duration * sampling_rate)
            delta = floor(((self.fixation_variability / 100.0) * samples) / 2)

            durations = [
                randint(samples - delta, samples + delta)
                for _ in range(self.saccades_count + 2)
            ]

            first, *main, last = durations

            chunks = [zeros(first, dtype=int8)]
            current_angle = -floor(self.angle / 2)
            for duration in main:
                chunks.append(ones(duration, dtype=int8) * current_angle)
                current_angle *= -1
            chunks.append(zeros(last, dtype=int8))

            self._channel = hstack(chunks)
        return self._channel


    @property
    def channel(self) -> ndarray:
        return self._channel

    def position(self, sample: int) -> Position:
        if self._channel is not None and sample < len(self._channel):
            if self._orientation == Orientation.Horizontal:
                if self._channel[sample] < 0:
                    return Position.Left
                if self._channel[sample] > 0:
                    return Position.Right
                return Position.Center

            if self._orientation == Orientation.Vertical:
                if self._channel[sample] < 0:
                    return Position.Top
                if self._channel[sample] > 0:
                    return Position.Bottom
                return Position.Center

        return Position.Unknown

    @classmethod
    def from_json(cls, json: dict):
        json.pop('category')
        return cls(**json)

    def to_json(self, dump_channels: bool = True) -> dict:
        result = Stimulus.to_json(self) | {
            'angle': self._angle,
            'fixation_duration': self._fixation_duration,
            'fixation_variability': self._fixation_variability,
            'saccades_count': self._saccades_count,
            'orientation': self._orientation,
        }
        if dump_channels:
            result['channel'] = self._channel
        return result
