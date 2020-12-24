from enum import Enum, IntEnum
from typing import Union

from .base import Model


class Board(Enum):
    Unknown = 'unknown'
    OtoScreen = 'otoscreen'
    OpenBCI_Cyton = 'cyton'
    Synthetized = 'synthetized'


class SampleRate(IntEnum):
    Unknown = 0
    SR250 = 250
    SR500 = 500
    SR1000 = 1000
    SR2000 = 2000
    SR4000 = 4000
    SR8000 = 8000
    SR16000 = 16000


class _Channel:

    def __init__(
        self,
        index: int,
        active: bool,
        gain: int = 24
    ):
        assert isinstance(index, int)
        self._index = index

        assert isinstance(active, bool)
        self._active = active

        assert isinstance(gain, int)
        self._gain = gain

    @property
    def index(self) -> int:
        return self._index

    @property
    def active(self) -> bool:
        return self._active

    @property
    def gain(self) -> int:
        return self._gain

    @classmethod
    def from_json(cls, json: dict):
        return cls(**json)

    def to_json(self) -> dict:
        return {
            'index': self._index,
            'active': self._active,
            'gain': self._gain,
        }


class _Channels:

    def __init__(self, channels: list[dict]):
        assert isinstance(channels, list)
        for channel in channels:
            assert isinstance(channel, dict)
        self._channels = [
            _Channel(**channel)
            for channel in channels
        ]

    def __len__(self) -> int:
        return len(self._channels)

    def __getitem__(self, index) -> _Channel:
        return self._channels[index]

    @classmethod
    def from_json(cls, json: list[dict]):
        return cls(json)

    def to_json(self) -> dict:
        return [
            channel.to_json()
            for channel in self._channels
        ]


class Recorder(Model):

    def __init__(
        self,
        board: Union[str, Board] = Board.Unknown,
        sample_rate: Union[int, SampleRate] = SampleRate.Unknown,
        channels: list[dict] = []
    ):

        if isinstance(board, str):
            board = Board(board)
        self._board = board

        if isinstance(sample_rate, int):
            sample_rate = SampleRate(sample_rate)
        self._sample_rate = sample_rate

        assert isinstance(channels, list)
        for channel in channels:
            assert isinstance(channel, dict)
        self._channels = _Channels(channels)

    @property
    def board(self) -> Board:
        return self._board

    @board.setter
    def board(self, value: Union[str, Board]):
        if isinstance(value, str):
            value = Board(value)
        self._board = value

    @property
    def sample_rate(self) -> SampleRate:
        return self._sample_rateA

    @sample_rate.setter
    def sample_rate(self, value: Union[int, SampleRate]):
        if isinstance(value, int):
            value = SampleRate(value)
        self._sample_rate = value

    @property
    def channels(self) -> _Channels:
        return self._channels

    @classmethod
    def from_json(cls, json: dict):
        return cls(**json)

    def to_json(self) -> dict:
        return {
            'board': self._board,
            'sample_rate': self._sample_rate,
            'channels': self._channels.to_json()
        }
