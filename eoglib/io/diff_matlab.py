from datetime import datetime
from os.path import getctime

from numpy import mean
from scipy.io import loadmat

from eoglib.models import Record, Subject, Test, Channel, SaccadicStimulus
from eoglib.models import SubjectStatus
from eoglib.models import ChannelCategory, ChannelSource, ChannelOrientation


_STATUS_TRANSLATION = {
    'S': SubjectStatus.Healthy,
    'E': SubjectStatus.Sick,
}


class DiffMatlabFormat:

    @classmethod
    def load(cls, path: str, noise: float = None) -> Record:
        data = loadmat(path)

        sampling_interval = data['tSm'][0][0]

        tests = []
        for record in range(int(data['cnRg'][0][0])):
            Y = data['yS'][0][record].flatten()
            Y0 = data['y0S'][0][record].flatten()

            # Normalizing the signals
            Y -= mean(Y)
            Y0 -= mean(Y0)

            test = Test(
                stimulus=SaccadicStimulus(
                    angle=data['nmFichero1'][0]
                ),
                parameters={
                    'velocity_threshold': data['vThr'][0][0]
                }
            )

            test[
                ChannelCategory.Time,
                ChannelOrientation.Both,
                ChannelSource.Both
            ] = Channel(
                data=data['xS'][0][record].flatten(),
                step=sampling_interval
            )

            test[
                ChannelCategory.Position,
                ChannelOrientation.Horizontal,
                ChannelSource.Recorded
            ] = Channel(
                data=Y,
                step=sampling_interval
            )

            test[
                ChannelCategory.Position,
                ChannelOrientation.Horizontal,
                ChannelSource.Reference
            ] = Channel(
                data=Y0,
                step=sampling_interval
            )

            test[
                ChannelCategory.Velocity,
                ChannelOrientation.Horizontal,
                ChannelSource.Reference
            ] = Channel(
                data=data['vS'][0][record].flatten(),
                step=sampling_interval
            )

            tests.append(test)

        record = Record(
            filename=data['nmFichero1'][0],
            recorded_at=datetime.fromtimestamp(getctime(path)),
            subject=Subject(
                status=_STATUS_TRANSLATION.get(data['Cat'][0], SubjectStatus.Unknown),
            ),
            tests=tests,
            calibration={
                ChannelOrientation.Horizontal: 1.0
            },
            parameters={
                'saccades_count': int(data['cnSc'][0][0]),
                'noise': float(path.split('_')[-2]) if noise is None else noise,
            }
        )
        return record
