from typing import Union

from numpy import ndarray

from .annotations import Annotation
from .base import Model
from .channels import Channel
from .stimulus import Stimulus


_CHANNEL_SNAKE_DICT = Channel.snake_names_dict()


class _ChannelManager:

    def __init__(self, channel: Channel, data: ndarray):
        self._channel = channel
        self._data = data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._data[key]

        if isinstance(key, Annotation):
            return self._data[key.onset:key.offset]

        if isinstance(key, tuple) and len(key) == 2:
            if isinstance(key[0], int) and isinstance(key[1], int):
                return self._data[key[0]:key[1]]

        raise IndexError('Index type not supported')

    def __setitem__(self, key, value):
        raise AttributeError('This attribute is inmutable')

    @property
    def channel(self) -> Channel:
        return self._channel

    @property
    def array(self) -> ndarray:
        return self._data


class _ChannelsDictionary(dict):

    def __init__(self, channels: dict[Channel, Union[str, ndarray]], *args):
        dict.__init__(self, *args)

        self._channels = channels
        self._managers: dict[Channel, _ChannelManager] = {}

    def __getattr__(self, name: str):
        if name not in _CHANNEL_SNAKE_DICT:
            raise AttributeError(f'{name} is not a valid attribute')
        channel = _CHANNEL_SNAKE_DICT[name]
        if channel not in self._managers and channel in self._channels:
            data = self._channels[channel]
            if isinstance(data, ndarray):
                self._managers[channel] = _ChannelManager(channel, data)
        return self._managers.get(channel, None)

    def __setattr__(self, name: str, value: ndarray):
        if name in _CHANNEL_SNAKE_DICT:
            channel = _CHANNEL_SNAKE_DICT[name]
            self._channels[channel] = value
        else:
            dict.__setattr__(name, value)

    def __getitem__(self, key):
        if isinstance(key, Channel):
            return self._channels[key]

        raise IndexError('Index type not supported')

    def __setitem__(self, key, value):
        if isinstance(key, Channel):
            assert isinstance(value, (str, ndarray))
            self._channels[key] = value
        else:
            raise IndexError('Index type not supported')


class Test(Model):

    def __init__(
        self,
        stimulus: Stimulus = Stimulus(False),
        channels: dict[Channel, Union[str, ndarray]] = {},
        annotations: list[Annotation] = [],
        study = None,
        **parameters
    ):
        assert isinstance(stimulus, Stimulus)
        self._stimulus = stimulus

        assert isinstance(channels, dict)
        for key, value in channels.items():
            assert isinstance(key, Channel)
            assert isinstance(value, (str, ndarray))
        self._channels = channels
        self._channels_dictionary = _ChannelsDictionary(channels)

        assert isinstance(annotations, list)
        for annotation in annotations:
            assert isinstance(annotation, Annotation)
        self._annotations = annotations

        self._study = study
        self._parameters = parameters

    def __str__(self):
        return str(self._stimulus)

    def __len__(self):
        return len(self._annotations)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._annotations[key]

        if isinstance(key, str):
            return self._parameters[key]

        if isinstance(key, Channel):
            return self._channels_dictionary[key]

        raise IndexError('Index type not supported')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            assert isinstance(value, Annotation)
            self._annotations[key] = value
        elif isinstance(key, str):
            self._parameters = value
        elif isinstance(key, Channel):
            assert isinstance(value, (str, ndarray))
            self._channels_dictionary[key] = value
        else:
            raise IndexError('Index type not supported')

    @property
    def stimulus(self) -> Stimulus:
        return self._stimulus

    @stimulus.setter
    def stimulus(self, value: Stimulus):
        assert isinstance(value, Stimulus)
        self._stimulus = value

    @property
    def channels(self) -> _ChannelsDictionary:
        return self._channels_dictionary

    @channels.setter
    def channels(self, value: dict[Channel, Union[str, ndarray]]):
        assert isinstance(value, dict)
        for key, value in value.items():
            assert isinstance(key, (str, Channel))
            assert isinstance(value, ndarray)
        self._channels = value
        self._channels_dictionary = _ChannelsDictionary(value)

    @property
    def annotations(self) -> list[Annotation]:
        return self._annotations

    @annotations.setter
    def annotations(self, value: list[Annotation]):
        assert isinstance(value, list)
        for annotation in value:
            assert isinstance(annotation, Annotation)
        self._annotations = value

    @property
    def parameters(self) -> dict:
        return self._parameters

    @parameters.setter
    def parameters(val, value: dict):
        assert isinstance(value, dict)
        self._parameters = value

    def append(self, annotation: Annotation):
        assert isinstance(annotation, Annotation)
        self._annotations.append(annotation)

    def insert(self, index: int, annotation: Annotation):
        assert isinstance(annotation, Annotation)
        self._annotations.insert(index, annotation)

    def remove(self, annotation: Annotation):
        assert isinstance(annotation, Annotation)
        self._annotations.remove(annotation)

    def remove_index(self, index: int):
        self._annotations.remove(self._annotations[index])

    def pop(self, index: int) -> Annotation:
        result = self._annotations[index]
        self._annotations.remove(result)
        return result

    @classmethod
    def from_json(cls, json: dict, study = None):
        stimulus = Stimulus.from_json(json.pop('stimulus'))
        if 'channels' in json:
            channels = {
                Channel(key): value
                for key, value in json.pop('channels')
            }
        else:
            channels = {}
        annotations = [
            Annotation.from_json(annotation)
            for annotation in json.pop('annotations')
        ]

        parameters = json.pop('parameters')

        return cls(
            stimulus=stimulus,
            channels=channels,
            annotations=annotations,
            study=study,
            **parameters
        )

    def to_json(self, dump_channels: bool=True) -> dict:
        result = {
            'stimulus': self._stimulus.to_json(),
            'annotations': [
                annotation.to_json()
                for annotation in self._annotations
            ],
            'parameters': self._parameters,
        }
        if dump_channels:
            result['channels'] = self._channels
        return result
