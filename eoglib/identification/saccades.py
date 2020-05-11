from typing import Iterable

from numpy import abs, where, array
from sklearn.cluster import KMeans

from eoglib.models import Saccade


def _mask_identification(mask: array) -> Iterable[Saccade]:
    """Identify saccadic movement from a masked array

    In the array:
        True: The sample belong to a potential saccade
        False: The sample belong to a potential fixation

    Args:
        mask: Mask array of boolean values
    Yields:
        Saccade objects
    """
    first_fixation = where(mask == False)[0][0]

    m0 = mask[first_fixation:-1]
    m1 = mask[first_fixation+1:]

    onsets = (where((m0 ^ m1) & m1) + first_fixation + 1).ravel()
    offsets = (where((m0 ^ m1) & m0) + first_fixation + 1).ravel()

    for onset, offset in zip(onsets, offsets):
        yield Saccade(
            onset=onset,
            offset=offset
        )


def _join_by_threshold(
    events: Iterable['Events'], 
    threshold: int
) -> Iterable[Saccade]:
    """Join events if are close enough

    Args:
        events: Iterable with candidate events
        threshold: Proximity threshold in samples
    Yields:
        Event objects
    """
    current = None
    for event in events:
        if current is None:
            current = event
        elif current.category != event.category:
            yield current
            current = event
        elif (event.onset - current.offset) <= threshold:
            current.offset = event.offset
        else:
            yield current
            current = event

    if current is not None:
        yield current


def threshold_identification(velocities: array, threshold: float = 30.0, **kwargs) -> Iterable[Saccade]:
    """Traditional velocity threshold saccade identification

    Args:
        velocities: Velocities profile of the eye movement
        threshold: Velocity threshold used as minimal value to set the occurrence of a saccade
    Yields:
        Saccade objects
    """
    mask = abs(velocities) >= threshold
    yield from _mask_identification(mask)


def kmeans_identification(velocities: array, **kwargs) -> Iterable[Saccade]:
    """Identify impulses from velocity profiles in eye movement signals

    This method identify impulses using the KMeans clustering algorithm.
    The idea behind this method is try to separate high velocity samples from low velocity ones into 2 clusters using KMeans.

    Contrary to Nyström approach we set the onset and offset points when the velocity cannot decrease no more, so there is no
    need for thresholds.

    Args: 
        velocities: Velocities profile of the eye movement
    Yields:
        Saccade objects
    """
    estimator = KMeans(n_clusters=2)
    abs_velocities = abs(velocities)
    labels = estimator.fit_predict(abs_velocities.reshape((len(abs_velocities), 1)))

    inverted = abs_velocities[labels == 1].mean() < abs_velocities[labels == 0].mean()
    if inverted:
        labels = abs(labels - 1)

    mask = labels == 1
    yield from _mask_identification(mask)


def identify_by_velocity(
    velocities: array, 
    method: str='kmeans', 
    join_threshold: int = None,
    **methodArgs
) -> Iterable[Saccade]:
    """Identify saccadic impulses using the velocity profile

    Args: 
        velocities: Velocities profile of the eye movement
        method: Method used for perform the identification. Options ['threshold', 'kmeans']
        join_threshold: Samples distance between saccades to be considered as single event
    Yields:
        Saccade objects
    """ 
    method_func = {
        'kmeans': kmeans_identification,
        'threshold': threshold_identification,
    }.get(method, kmeans_identification)

    saccades = method_func(velocities, **methodArgs)

    if join_threshold is not None:
        saccades = _join_by_threshold(saccades, join_threshold)

    yield from saccades 

