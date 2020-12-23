from datetime import datetime

from .base import Model
from .stimulus import Stimulus


class Protocol(Model):

    def __init__(
        self,
        stimuli: list[Stimulus],
        version: str = '1.0',
        created_at: datetime = datetime.now(),
        **parameters
    ):
        super(Protocol, self).__init__(**parameters)

        self._stimuli = stimuli
        self._version = version
        self._created_at = created_at

    def __len__(self):
        return len(self._stimuli)

    def __getitem__(self, index: int) -> Stimulus:
        return self._stimuli[index]

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

    @classmethod
    def from_json(cls, json: dict):
        parameters = json.pop('parameters')
        return cls(**json, **parameters)

    def to_json(self, template: bool = False) -> dict:
        stimuli = []
        for stimulus in self._stimuli:
            current = stimulus.to_json()
            if template:
                current.pop('channel')
            stimuli.append(current)

        return {
            'version': self._version,
            'created_at': self._created_at,
            'stimuli': self._stimuli,
        } | Model.to_json(self)
