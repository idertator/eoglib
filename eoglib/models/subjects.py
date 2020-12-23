from datetime import date
from enum import IntEnum
from typing import Any, Union

from .base import Model


class Gender(IntEnum):
    Unknown = 0
    Male = 1
    Female = 2

    @property
    def label(self) -> str:
        return {
            Gender.Unknown: _('Desconocido'),
            Gender.Male: _('Masculino'),
            Gender.Female: _('Femenino'),
        }[self]


class Status(IntEnum):
    Unknown = 0
    Control = 1
    Presymptomatic = 2
    Sick = 3

    @property
    def label(self) -> str:
        return {
            Status.Unknown: _('Desconocido'),
            Status.Control: _('Control'),
            Status.Presymptomatic: _('Presintomático'),
            Status.Sick: _('Enfermo'),
        }[self]


class Subject(Model):

    def __init__(
        self,
        name: str = '',
        gender: Union[int, Gender] = Gender.Unknown,
        status: Union[int, Status] = Status.Unknown,
        borndate: date = date.today(),
        **parameters
    ):
        super(Subject, self).__init__(**parameters)

        assert isinstance(name, str)
        self._name = name

        if isinstance(gender, int):
            gender = Gender(gender)
        assert isinstance(gender, Gender)
        self._gender = gender

        if isinstance(status, int):
            status = Status(status)
        assert isinstance(status, Status)
        self._status = status

        assert isinstance(borndate, date)
        self._borndate = borndate

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._parameters[key]
        raise IndexError('Index type is not supported')

    def __setitem__(self, key, value):
        if isinstance(key, str):
            self._parameters[key] = value
        else:
            raise IndexError('Index type is not supported')

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        assert isinstance(value, str)
        self._name = value

    @property
    def gender(self) -> Gender:
        return self._gender

    @gender.setter
    def gender(self, value: Union[int, Gender]):
        if isinstance(value, int):
            value = Gender(value)
        assert isinstance(value, Gender)
        self._gender = value

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Union[int, Status]):
        if isinstance(value, int):
            value = Status(value)
        assert isinstance(value, Status)
        self._status = value

    @property
    def borndate(self) -> date:
        return self._borndate

    @borndate.setter
    def borndate(self, value: date):
        assert isinstance(value, date)
        self._borndate = date

    @property
    def age(self) -> int:
        today = date.today()
        if (borndate := self._borndate) is not None:
            years = today.year - borndate.year
            if (today.month, today.day) < (borndate.month, borndate.day):
                years -= 1
            return years
        return 0

    @property
    def code(self) -> str:
        name = self.name.upper().strip().split(' ')
        while len(name) > 3:
            name.remove(name[1])

        initials = ''
        if len(name) == 1:
            initials = name[0][0:3]
        else:
            for text in name:
                initials += text[0]

        return initials + self._borndate.strftime('%d%m%Y')

    @classmethod
    def from_json(cls, json: dict):
        parameters = json.pop('parameters')
        return cls(**json, **parameters)

    def to_json(self) -> dict:
        return Model.to_json(self) | {
            'name': self._name,
            'gender': self._gender,
            'status': self._status,
            'borndate': self._borndate,
        }
