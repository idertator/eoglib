from datetime import date, datetime
from enum import Enum
from typing import Any, Union

from .base import Model


class IndexedEnum(Enum):

    @classmethod
    def from_index(cls, index: int):
        for idx, value in enumerate(type(self)):
            if index == idx:
                return value
        return None

    @property
    def index(self) -> int:
        for idx, value in enumerate(type(self)):
            if value == self:
                return idx
        return -1


class Gender(IndexedEnum):
    Unknown = 'unknown'
    Male = 'male'
    Female = 'female'

    @property
    def label(self) -> str:
        return {
            Gender.Unknown: _('Desconocido'),
            Gender.Male: _('Masculino'),
            Gender.Female: _('Femenino'),
        }[self]



class Status(IndexedEnum):
    Unknown = 'unknown'
    Control = 'control'
    Presymptomatic = 'presymptomatic'
    Sick = 'sick'

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
        gender: Union[str, Gender] = Gender.Unknown,
        status: Union[str, Status] = Status.Unknown,
        borndate: date = date.today()
    ):
        assert isinstance(name, str)
        self._name = name

        if isinstance(gender, str):
            gender = Gender(gender)
        assert isinstance(gender, Gender)
        self._gender = gender

        if isinstance(status, str):
            status = Status(status)
        assert isinstance(status, Status)
        self._status = status

        if isinstance(borndate, str):
            borndate = datetime.strptime(borndate, '%Y-%m-%d').date()
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
    def gender(self, value: Union[str, Gender]):
        if isinstance(value, str):
            value = Gender(value)
        assert isinstance(value, Gender)
        self._gender = value

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Union[str, Status]):
        if isinstance(value, str):
            value = Status(value)
        assert isinstance(value, Status)
        self._status = value

    @property
    def borndate(self) -> date:
        return self._borndate

    @borndate.setter
    def borndate(self, value: date):
        assert isinstance(value, date)
        self._borndate = value

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
    def initials(self) -> str:
        return ''.join((
            name[0]
            for name in self._name.upper().split()
        ))

    @property
    def code(self) -> str:
        return self.initials + self._borndate.strftime('%d%m%Y')

    @classmethod
    def from_json(cls, json: dict):
        return cls(**json)

    def to_json(self) -> dict:
        return {
            'name': self._name,
            'gender': self._gender,
            'status': self._status,
            'borndate': self._borndate,
        }
