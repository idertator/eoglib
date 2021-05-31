from datetime import datetime
from os.path import getctime

from numpy import mean
from scipy.io import loadmat

from eoglib.models import (Board, Channel, Recorder, SaccadicStimulus, Status,
                           Study, Subject, Test)

_STATUS_TRANSLATION = {
    'S': Status.Control,
    'E': Status.Sick,
}


def load_diff(path: str, noise: float = None) -> Study:
    data = loadmat(path)

    sampling_interval = data['tSm'][0][0]
    sample_rate = 1000 // int(sampling_interval)

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
            channels={
                Channel.Time: data['xS'][0][record].flatten(),
                Channel.Horizontal: Y,
                Channel.PositionReference: Y0,
                Channel.VelocityReference: data['vS'][0][record].flatten(),
            },
            velocity_threshold=data['vThr'][0][0]
        )

        tests.append(test)

    study = Study(
        recorded_at=datetime.fromtimestamp(getctime(path)),
        recorder=Recorder(
            board=Board.Synthetized,
            sample_rate=sample_rate
        ),
        subject=Subject(
            status=_STATUS_TRANSLATION.get(data['Cat'][0], Status.Unknown),
        ),
        tests=tests,
        saccades_count=int(data['cnSc'][0][0]),
        noise=float(path.split('_')[-2]) if noise is None else noise
    )

    return study
