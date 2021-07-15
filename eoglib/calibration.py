from collections import defaultdict

from numpy import arange, array, isnan, mean
from scipy.signal import medfilt

from eoglib.biomarkers import compute_saccadic_biomarkers
from eoglib.consts import AMPLITUDE_VALID_RANGES
from eoglib.differentiation import super_lanczos_11
from eoglib.errors import CalibrationError
from eoglib.identification import identify_saccades_by_kmeans
from eoglib.models import Channel, Study
from eoglib.stimulation import saccadic_previous_transition_index
from eoglib.filtering import butter_filter


def calibrate(study: Study, ignore_errors: bool = False) -> dict[Channel, float]:
    calibration = defaultdict(list)

    coeffs = []
    for test in study:
        if test.stimulus.calibration:
            amplitudes = []
            channel = Channel.Horizontal

            if channel in test:
                S = None
                if Channel.Stimulus in test:
                    S = test[Channel.Stimulus]
                Y = butter_filter(test[channel], test.sample_rate, 30)
                X = arange(len(Y)) * test.sampling_interval
                V = super_lanczos_11(Y, test.sampling_interval)
                Vf = butter_filter(V, test.sample_rate, 19)
                saccades = list(identify_saccades_by_kmeans(Vf))

                angle = test.stimulus.angle

                new_saccades = []
                for saccade in saccades:
                    duration = X[saccade.offset] - X[saccade.onset]
                    if duration < 0.04:
                        continue

                    if S is not None:
                        transition_index = saccadic_previous_transition_index(S, saccade.onset)
                        latency = X[saccade.onset] - X[transition_index]
                        amplitude = abs(Y[saccade.offset] - Y[saccade.onset])

                        if latency > 1:
                            continue

                    saccade['angle'] = angle
                    saccade['transition'] = transition_index
                    saccade['latency'] = latency
                    saccade['duration'] = X[saccade.offset] - X[saccade.onset]
                    saccade['amplitude'] = amplitude

                    new_saccades.append(saccade)
                    amplitudes.append(amplitude)

                test.annotations = new_saccades

            coeffs.append(angle / mean(amplitudes))

    coeff = mean(coeffs)

    # Refine calibration
    for test in study:
        if test.stimulus.calibration:
            angle = test.stimulus.angle
            channel = Channel.Horizontal

            AMPLITUDE_MIN, AMPLITUDE_MAX = AMPLITUDE_VALID_RANGES[angle]

            new_saccades = []
            transitions = set()
            for saccade in test:
                saccade['amplitude'] *= coeff

                if saccade['amplitude'] < AMPLITUDE_MIN or saccade['amplitude'] > AMPLITUDE_MAX:
                    continue

                if saccade['latency'] > 0.5:
                    continue

                if saccade['transition'] in transitions:
                    continue

                transitions.add(saccade['transition'])
                new_saccades.append(saccade)

            test.annotations = new_saccades

    # Recalculate coefficients
    for test in study:
        if test.stimulus.calibration:
            angle = test.stimulus.angle
            channel = Channel.Horizontal
            Y = butter_filter(test[channel], test.sample_rate, 30)

            amplitudes = array([
                abs(Y[saccade.offset] - Y[saccade.onset])
                for saccade in test
            ])

            if amplitudes.any():
                coeff = float(angle) / mean(amplitudes)

                if not isnan(coeff):
                    calibration[channel].append(coeff)

    # Calculate final coefficients
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
