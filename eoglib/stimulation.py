from numpy import array


def saccadic_previous_transition_index(stimulus: array, index: int) -> int:
    current = index
    while current > 0 and stimulus[current] == stimulus[current - 1]:
        current -= 1
    return current


def saccadic_next_transition_index(stimulus: array, index: int) -> int:
    current = index
    last = len(stimulus) - 1
    while current < last and stimulus[current] == stimulus[current + 1]:
        current += 1
    return current
