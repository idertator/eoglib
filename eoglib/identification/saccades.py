from typing import Iterable

from numpy import abs, argwhere, array

from eoglib.models import Saccade


def velocity_threshold_identification(velocities: array, threshold: float = 30.0) -> Iterable[Saccade]:
    """Traditional velocity threshold saccade identification

    Args:
        velocities: Velocities profile of the eye movement
        threshold: Velocity threshold used as minimal value to set the occurrence of a saccade
    Yields:
        Saccade objects
    """
    mask = abs(velocities) >= threshold
    m0 = mask[:-1]
    m1 = mask[1:]
    onsets = (argwhere((m0 ^ m1) & m1) + 1).ravel()
    offsets = (argwhere((m0 ^ m1) & m0) + 1).ravel()
    for onset, offset in zip(onsets, offsets):
        yield Saccade(
            onset=onset,
            offset=offset
        )

