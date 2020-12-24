from typing import Union

from numpy import ndarray

from .annotations import Annotation
from .base import Model
from .channels import Channel
from .stimulus import Stimulus


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
        elif isinstance(key, str):
            return self._parameters[key]
        elif isinstance(key, Channel):
            return self._channels[key]
        else:
            raise IndexError('Index type not supported')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            assert isinstance(value, Annotation)
            self._annotations[key] = value
        elif isinstance(key, str):
            self._parameters = value
        elif isinstance(key, Channel):
            assert isinstance(value, (str, ndarray))
            self._channels[key] = value
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
    def channels(self) -> dict[Channel, Union[str, ndarray]]:
        return self._channels

    @channels.setter
    def channels(self, value: dict[Channel, Union[str, ndarray]]):
        assert isinstance(value, dict)
        for key, value in value.items():
            assert isinstance(key, (str, Channel))
            assert isinstance(value, ndarray)
        self._channels = value

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
        channels = {
            Channel(key): value
            for key, value in json.pop('channels')
        }
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

    def to_json(self) -> dict:
        return {
            'stimulus': self._stimulus.to_json(),
            'channels': self._channels,
            'annotations': [
                annotation.to_json()
                for annotation in self._annotations
            ],
            'parameters': self._parameters,
        }
