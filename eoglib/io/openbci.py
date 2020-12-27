from numpy import ndarray, array, int32, int32


def load_openbci(filename: str) -> tuple[ndarray, ndarray, ndarray]:
    def mV(sample: str) -> int:
        return int(f'0x{sample}', 0)

    current_stimulus = 2

    horizontal, vertical, stimulus = [], [], []
    with open(path, 'rt') as f:
        for line in f:
            components = line.strip().split(',')
            if len(components) == 12:
                horizontal.append(mV(components[1]))
                vertical.append(mV(components[2]))

                sample_stimulus = components[-3]
                if sample_stimulus[-1] != '0':
                    current_stimulus = int(sample_stimulus[-1])

                stimulus.append({
                    1: 1,
                    2: 0,
                    3: -1,
                }[current_stimulus])

    horizontal = array(horizontal, dtype=int32)[1:]
    horizontal -= int(mean(horizontal))

    vertical = array(vertical, dtype=int32)[1:]
    vertical -= int(mean(vertical))

    stimulus = array(stimulus, dtype=int32)[1:]

    return horizontal, vertical, stimulus
