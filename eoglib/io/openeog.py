from dataclasses import dataclass
from math import log10
from struct import unpack

from numpy import array, int32, max, mean, min, ndarray, uint32

from eoglib.filtering import notch_filter
from eoglib.models import StimulusPosition

_DEFAULT_GAIN = 24
_SAMPLE_VOLTS_SCALE = (4.5 / _DEFAULT_GAIN / (2**23 - 1))


def mV(sample: int) -> int:
    return int(sample * _SAMPLE_VOLTS_SCALE)


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
        timestamp, index, horizontal_channel, vertical_channel =  unpack('>I3s3s3s', data[1:-2])
        position = unpack('>H', data[-2:])[0]

        return cls(
            header=header,
            timestamp=timestamp,
            index=unpack('>I', b'\00' + index)[0],
            horizontal_channel=unpack('>I', b'\00' + horizontal_channel)[0],
            vertical_channel=unpack('>I', b'\00' + vertical_channel)[0],
            position=StimulusPosition(position)
        )


def load_openeog(filename: str, apply_filter: bool = True) -> list[tuple[ndarray, ndarray, ndarray, ndarray, ndarray]]:
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

        if apply_filter:
            horizontal_samples = notch_filter(horizontal_samples, 1000, 50).astype(int32)

        vertical_samples = array(vertical_samples, dtype=int32)
        vertical_samples -= int(mean(vertical_samples))

        if apply_filter:
            vertical_samples = notch_filter(vertical_samples, 1000, 50).astype(int32)

        min_h = abs(horizontal_samples.min())
        max_h = abs(horizontal_samples.max())

        max_horizontal =  max([min_h, max_h])
        horizontal_scale =  10 ** int(log10(max_horizontal))

        stimulus = array(positions, dtype=int32) * horizontal_scale

        result.append((
            timestamps[1:],
            indexes[1:] - 1,
            horizontal_samples[1:],
            vertical_samples[1:],
            positions[1:]
        ))

    return result
