from datetime import datetime
from math import radians, tan

from .base import Model
from .stimulus import Stimulus, SaccadicStimulus, Category


class Protocol(Model):

    def __init__(
        self,
        stimuli: list[Stimulus],
        name: str = 'Default',
        version: str = '1.0',
        created_at: datetime = datetime.now()
    ):
        assert isinstance(stimuli, list)
        for stimulus in stimuli:
            assert isinstance(stimulus, Stimulus)
        self._stimuli = stimuli

        assert isinstance(name, str)
        self._name = name

        assert isinstance(version, str)
        self._version = version

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        assert isinstance(created_at, datetime)
        self._created_at = created_at

    def __len__(self):
        return len(self._stimuli)

    def __getitem__(self, index: int) -> Stimulus:
        return self._stimuli[index]

    def insert(self, index: int, stimulus: Stimulus):
        self._stimuli.insert(index, stimulus)

    def remove(self, index: int):
        del self._stimuli[index]

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        assert isinstance(value, str)
        self._name = value

    @property
    def version(self) -> str:
        return self._version

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def max_angle(self) -> float:
        return float(
            max(
                stimulus.angle
                for stimulus in self._stimuli
            )
        )

    def distance_to_subject(self, screen_distance: float) -> float:
        angle = self.max_angle
        return (screen_distance / 2.0) / tan(radians(angle / 2.0))

    @classmethod
    def from_json(cls, json: dict):
        stimuli = json.pop('stimuli')
        json['stimuli'] = []
        for stimulus in stimuli:
            if Category(stimulus['category']) == Category.Saccadic:
                json['stimuli'].append(SaccadicStimulus.from_json(stimulus))
        return cls(**json)

    def to_json(self, template: bool = False) -> dict:
        stimuli = []
        for stimulus in self._stimuli:
            current = stimulus.to_json()
            if template:
                current.pop('channel')
            stimuli.append(current)

        return {
            'version': self._version,
            'name': self._name,
            'created_at': self._created_at,
            'stimuli': stimuli,
        }
