from dataclasses import dataclass, field
from datetime import date
from enum import IntEnum
from typing import Dict, Any


class SubjectStatus(IntEnum):
    Unknown = 0
    Healthy = 1
    Presymptomatic = 2
    Sick = 3


@dataclass
class Subject:
    fullname: str = ''
    status: SubjectStatus = SubjectStatus.Unknown
    borndate: date = None
    parameters: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.parameters[key]
        raise IndexError('Index type is not supported')

    def __setitem__(self, key, value):
        if isinstance(key, str):
            self.parameters[key] = value
        else:
            raise IndexError('Index type is not supported')

