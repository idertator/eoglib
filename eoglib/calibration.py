from collections import defaultdict

from numpy import arange, array, isnan, mean
from scipy.signal import medfilt

from eoglib.differentiation import super_lanczos_11
from eoglib.errors import CalibrationError
from eoglib.identification import identify_saccades_by_kmeans
from eoglib.models import Channel, Study
from eoglib.stimulation import saccadic_previous_transition_index
from eoglib.filtering import butter_filter


def calibrate(study: Study, ignore_errors: bool = False) -> dict[Channel, float]:
    calibration = defaultdict(list)

    for test in study:
        if test.stimulus.calibration:
            for channel in (
                Channel.Horizontal,
                # Channel.Vertical
            ):
                if channel in test:

                    S = None
                    if Channel.Stimulus in test:
                        S = test[Channel.Stimulus]
                    Y = butter_filter(test[channel], test.sample_rate, 30)
                    X = arange(len(Y)) * test.sampling_interval
                    V = super_lanczos_11(Y, test.sampling_interval)
                    saccades = list(identify_saccades_by_kmeans(V))

                    new_saccades = []
                    for saccade in saccades:
                        duration = X[saccade.offset] - X[saccade.onset]
                        if duration < 0.04:
                            continue

                        if S is not None:
                            transition_index = saccadic_previous_transition_index(S, saccade.onset)
                            latency = X[saccade.onset] - X[transition_index]

                            if latency > 1:
                                continue

                        new_saccades.append(saccade)

                    if saccades := new_saccades[1:-1]:
                        amplitudes = array([
                            abs(Y[saccade.offset] - Y[saccade.onset])
                            for saccade in saccades
                        ])

                        if amplitudes.any():
                            angle = test.stimulus.angle

                            coeff = float(angle) / mean(amplitudes)

                            if not isnan(coeff):
                                calibration[channel].append(coeff)

    result = {}

    for channel in (
        Channel.Horizontal,
        Channel.Vertical
    ):
        if channel in calibration:
            data = calibration[channel]

            if len(data) == 0:
                if not ignore_errors:
                    raise CalibrationError(f'No calibration data could be could be calculated for {channel.name} channel')

            elif len(data) == 1:
                if not ignore_errors:
                    raise CalibrationError(f'Only one calibration found for {channel.name} channel')
                result[channel] = data[0]

            else:
                diff = min(data) / max(data)

                if diff < 0.8 and not ignore_errors:
                    raise CalibrationError(f'The calibration difference ratio for {channel.name} channel is {diff:.4f} (<0.8)')

                result[channel] = mean(data)

    return result
