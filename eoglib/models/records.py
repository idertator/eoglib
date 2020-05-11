from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Type

from numpy import array

from .channels import ChannelOrientation
from .subjects import Subject
from .tests import Test


@dataclass
class Record:
    filename: str = ''
    recorded_at: datetime = None 
    subject: Subject = None
    tests: List[Test] = field(default_factory=list)
    calibration: Dict[ChannelOrientation, float] = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)

    def __len__(self):
        return len(self.tests)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.tests[key]
        elif isinstance(key, str):
            return self.parameters[key]
        raise IndexError('Index type is not supported')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if not isinstance(value, Test):
                raise TypeError('The value must be of type Test')
            self.tests[key] = value
        elif isinstance(key, str):
            self.parameters[key] = value
            self.tests[key] = value
        else:
            raise IndexError('Index type is not supported')

    def __add__(self, value):
        if not isinstance(value, Test):
            raise TypeError('The value must be of type Test')
        self.tests.append(value)

