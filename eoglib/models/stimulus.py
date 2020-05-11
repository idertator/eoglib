from dataclasses import dataclass
from enum import IntEnum


class StimulusCategory(IntEnum):
    Unknown = 0
    Saccadic = 1


@dataclass
class Stimulus:
    category: StimulusCategory = StimulusCategory.Unknown


@dataclass
class SaccadicStimulus(Stimulus):
    category: StimulusCategory = StimulusCategory.Saccadic
    angle: int = None

