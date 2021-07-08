from dataclasses import dataclass
from math import floor, log10
from struct import unpack

from numpy import array, int32, mean, ndarray, uint32
from numpy.polynomial import Polynomial
from scipy.signal import medfilt

from eoglib.filtering import notch_filter
from eoglib.models import StimulusPosition

OMIT_TIME = 1000


@dataclass
class Sample:
    header: int
    timestamp: int
    index: int
    horizontal_channel: int
    vertical_channel: int
    position: StimulusPosition

    @classmethod
    def build(cls, data: bytes):
        header = data[0]
        timestamp, index, horizontal_channel, vertical_channel = unpack('>I3s3s3s', data[1:-2])
        position = unpack('>H', data[-2:])[0]

        return cls(
            header=header,
            timestamp=timestamp,
            index=unpack('>I', b'\00' + index)[0],
            horizontal_channel=unpack('>I', b'\00' + horizontal_channel)[0],
            vertical_channel=unpack('>I', b'\00' + vertical_channel)[0],
            position=StimulusPosition(position)
        )


def load_openeog(
    filename: str,
    apply_filter: bool = True,
    fix_drift: bool = True,
    medfilt_size: int = None
) -> list[tuple[ndarray, ndarray, ndarray, ndarray, ndarray]]:
    test_list = []

    sample_list = None
    sample = None

    with open(filename, 'rb') as f:
        while buff := f.read(16):
            if buff[0] == 0x82 or len(buff) < 16:
                break

            sample = Sample.build(buff)

            if sample.header == 0x00:
                sample_list.append(sample)
            elif sample.header == 0x80:
                sample_list = []
            elif sample.header == 0x81:
                test_list.append(sample_list)

    result = []

    for sample_list in test_list:
        timestamps = []
        indexes = []
        horizontal_samples = []
        vertical_samples = []
        positions = []

        for sample in sample_list:
            timestamps.append(sample.timestamp)
            indexes.append(sample.index)
            horizontal_samples.append(sample.horizontal_channel)
            vertical_samples.append(sample.vertical_channel)
            positions.append(sample.position.stimulus)

        timestamps = array(timestamps, dtype=uint32)
        indexes = array(indexes, dtype=uint32)

        horizontal_samples = array(horizontal_samples, dtype=int32)
        horizontal_samples -= int(mean(horizontal_samples))

        vertical_samples = array(vertical_samples, dtype=int32)
        vertical_samples -= int(mean(vertical_samples))

        timestamps = timestamps[OMIT_TIME:]
        indexes = indexes[OMIT_TIME:] - OMIT_TIME
        horizontal_samples = horizontal_samples[OMIT_TIME:]
        vertical_samples = vertical_samples[OMIT_TIME:]

        # if apply_filter:
        #     horizontal_samples = notch_filter(horizontal_samples, 1000, 50).astype(int32)
        #     vertical_samples = notch_filter(vertical_samples, 1000, 50).astype(int32)

        if fix_drift:
            pfit, stats = Polynomial.fit(indexes, horizontal_samples, 2, full=True)
            horizontal_samples = horizontal_samples - pfit(indexes)

        if medfilt_size is not None:
            horizontal_samples = medfilt(horizontal_samples, medfilt_size)
            vertical_samples = medfilt(vertical_samples, medfilt_size)

        min_h = abs(horizontal_samples.min())
        max_h = abs(horizontal_samples.max())

        max_horizontal = max([min_h, max_h])
        horizontal_scale = 10 ** floor(log10(max_horizontal))

        stimulus = array(positions, dtype=int32) * horizontal_scale
        stimulus = stimulus[OMIT_TIME:]

        result.append((
            timestamps,
            indexes,
            horizontal_samples,
            vertical_samples,
            stimulus,
        ))

    return result
