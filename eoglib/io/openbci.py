from numpy import ndarray, array, int32, mean

from eoglib.models import StimulusPosition


def load_openbci(filename: str) -> tuple[ndarray, ndarray, ndarray]:
    def mV(sample: str) -> int:
        return int(f'0x{sample}', 0)

    current_stimulus = 0

    horizontal, vertical, stimulus = [], [], []

    center = StimulusPosition.Center.value

    with open(filename, 'rt') as f:
        initialized = False
        for line in f:
            components = line.strip().split(',')
            if len(components) == 12:
                sample_stimulus = components[-3]
                if sample_stimulus[-1] != '0':
                    current_stimulus = int(sample_stimulus[-1])

                if not initialized and current_stimulus != center:
                    continue

                initialized = True

                stimulus.append({
                    StimulusPosition.Left.value: -1,
                    StimulusPosition.Center.value: 0,
                    StimulusPosition.Right.value: 1,
                }[current_stimulus])

                horizontal.append(mV(components[1]))
                vertical.append(mV(components[2]))

    horizontal = array(horizontal, dtype=int32)[1:]
    horizontal -= int(mean(horizontal))

    vertical = array(vertical, dtype=int32)[1:]
    vertical -= int(mean(vertical))

    stimulus = array(stimulus, dtype=int32)[1:]

    return horizontal, vertical, stimulus
