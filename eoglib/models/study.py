from datetime import datetime
from typing import Union

from .base import Model
from .hardware import Recorder
from .subjects import Subject
from .channels import Channel
from .tests import Test


class Study(Model):

    def __init__(
        self,
        version: str = '1.0',
        recorded_at: Union[str, datetime] = datetime.now(),
        recorder: Recorder = Recorder(),
        subject: Subject = Subject(),
        calibration: dict[Channel, float] = None,
        protocol_name: str = '',
        tests: list[Test] = None,
        light_intensity: int = 0,
        ignore_calibration_errors: bool = False,
        **parameters
    ):
        assert isinstance(version, str)
        self._version = version

        if isinstance(recorded_at, str):
            recorded_at = datetime.fromisoformat(recorded_at)
        assert isinstance(recorded_at, datetime)
        self._recorded_at = recorded_at

        assert isinstance(recorder, Recorder)
        self._recorder = recorder

        assert isinstance(subject, Subject)
        self._subject = subject

        if calibration is None:
            self._calibration = {}
        else:
            assert isinstance(calibration, dict)
            for key, value in calibration.items():
                assert isinstance(key, (str, Channel))
                assert isinstance(value, float)
            self._calibration = calibration

        assert isinstance(protocol_name, str)
        self._protocol_name = protocol_name

        if tests is None:
            self._tests = []
        else:
            assert isinstance(tests, list)
            for test in tests:
                assert isinstance(test, Test)
            self._tests = tests

        assert isinstance(light_intensity, int)
        self._light_intensity = light_intensity

        assert isinstance(ignore_calibration_errors, bool)
        self._ignore_calibration_errors = ignore_calibration_errors

        self._parameters = parameters

    def __str__(self):
        return _('Recorded at {recorded_at} to {subject}').format(
            recorded_at=self._recorded_at.strftime('%d/%m%Y %H:%M'),
            subject=self._subject.name
        )

    def __len__(self):
        return len(self._tests)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._tests[key]
        elif isinstance(key, Channel):
            return self._calibration[key]
        else:
            raise IndexError('Index type not supported')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            assert isinstance(value, Test)
            self._tests[key] = value
        elif isinstance(key, Channel):
            assert isinstance(value, float)
            self._calibration[key] = value
        else:
            raise IndexError('Index type not supported')

    @property
    def recorder(self) -> Recorder:
        return self._recorder

    @recorder.setter
    def recorder(self, value: Recorder):
        assert isinstance(value, Recorder)
        self._recorder = value

    @property
    def subject(self) -> Subject:
        return self._subject

    @subject.setter
    def subject(self, value: Subject):
        assert isinstance(value, Subject)
        self._subject = value

    @property
    def calibration(self) -> dict[Channel, float]:
        if not self._calibration:
            from eoglib.calibration import calibrate
            self._calibration = calibrate(self, self._ignore_calibration_errors)
        return self._calibration

    @calibration.setter
    def calibration(self, value: dict[Channel, float]):
        assert isinstance(value, dict)
        for key, value in value.items():
            assert isinstance(key, (str, Channel))
            assert isinstance(value, float)
        self._calibration = value

    @property
    def protocol_name(self) -> str:
        return self._protocol_name

    @protocol_name.setter
    def protocol_name(self, value: str):
        assert isinstance(value, str)
        self._protocol_name = value

    @property
    def tests(self) -> list[Test]:
        return self._tests

    @tests.setter
    def tests(self, value: list[Test]):
        assert isinstance(value, list)
        for test in value:
            assert isinstance(test, Test)
        self._tests = value

    @property
    def light_intensity(self) -> int:
        return self._light_intensity

    @light_intensity.setter
    def light_intensity(self, value: int):
        assert isinstance(value, int)
        self._light_intensity = value

    @property
    def ignore_calibration_errors(self) -> bool:
        return self._ignore_calibration_errors

    @ignore_calibration_errors.setter
    def ignore_calibration_errors(self, value: bool):
        assert isinstance(value, bool)
        self._ignore_calibration_errors = value

    @property
    def parameters(self) -> dict:
        return self._parameters

    @parameters.setter
    def parameters(self, value: dict):
        assert isinstance(value, dict)
        self._parameters = value

    def append(self, test: Test):
        assert isinstance(test, Test)
        self._tests.append(test)

    def insert(self, index: int, test: Test):
        assert isinstance(test, Test)
        self._tests.insert(index, test)

    def remove(self, test: Test):
        assert isinstance(test, Test)
        self._tests.remove(test)

    def remove_index(self, index: int):
        self._tests.remove(self._tests[index])

    def pop(self, index: int) -> Test:
        result = self._tests[index]
        self._tests.remove(result)
        return result

    def identify_saccades_and_compute_biomarkers(self):
        from numpy import arange

        from eoglib.biomarkers import compute_saccadic_biomarkers
        from eoglib.calibration import saccadic_previous_transition_index
        from eoglib.differentiation import super_lanczos_11
        from eoglib.filtering import butter_filter
        from eoglib.identification import identify_saccades_by_kmeans

        for test in self._tests:
            S = test[Channel.Stimulus]
            X = arange(len(S)) * test.sampling_interval
            S = (S / abs(max(S)) * test.stimulus.angle)
            Yf = test.horizontal_channel
            V = super_lanczos_11(Yf, test.sampling_interval)
            VF = abs(butter_filter(V, test.sample_rate, 19))

            angle = test.stimulus.angle

            saccades = list(identify_saccades_by_kmeans(VF))

            # Compute approximated biomarkers
            for s in saccades:
                transition = saccadic_previous_transition_index(S, s.onset)
                latency = X[s.onset] - X[transition]
                amplitude = abs(Yf[s.onset] - Yf[s.offset])
                duration = X[s.offset] - X[s.onset]

                s['angle'] = angle
                s['transition'] = transition
                s['latency'] = latency
                s['amplitude'] = amplitude
                s['duration'] = duration

            # Exclude saccades which not fullfill minimal requirements of amplitude and latency
            AMPLITUDE_VALID_RANGES = {
                10: (7, 14),
                20: (17, 26),
                30: (26, 37),
                60: (50, 70),
            }

            AMPLITUDE_MIN, AMPLITUDE_MAX = AMPLITUDE_VALID_RANGES.get(
                angle,
                (angle - angle * 0.1, angle + angle * 0.1)
            )

            saccades = [
                s
                for s in saccades
                if (AMPLITUDE_MIN <= s['amplitude'] <= AMPLITUDE_MAX) and (s['latency'] <= 0.5)
            ]

            # Exclude saccades in the same stimulus transition
            # Prioritizing the one with lesser latency
            result = []
            transitions = set()
            for s in saccades:
                if s['transition'] not in transitions:
                    transitions.add(s['transition'])
                    result.append(s)

            saccades = result

            # Fine computation of saccadic biomarkers
            for s in saccades:
                compute_saccadic_biomarkers(s, Yf, test.sampling_interval)

            test.annotations = saccades

    @classmethod
    def from_json(cls, json: dict):
        recorder = Recorder.from_json(json.pop('recorder'))
        subject = Subject.from_json(json.pop('subject'))
        calibration = {
            Channel(key): value
            for key, value in json.pop('calibration')
        }

        tests = json.pop('tests')
        parameters = json.pop('parameters')

        study = cls(
            recorder=recorder,
            subject=subject,
            calibration=calibration,
            **json,
            **parameters
        )

        study.tests = [
            Test.from_json(test, study)
            for test in tests
        ]

        return study

    def to_json(self, dump_channels: bool = True) -> dict:
        return {
            'version': self._version,
            'recorded_at': self._recorded_at,
            'recorder': self._recorder.to_json(),
            'subject': self._subject.to_json(),
            'calibration': self._calibration,
            'protocol_name': self._protocol_name,
            'tests': [
                test.to_json(dump_channels)
                for test in self._tests
            ],
            'light_intensity': self._light_intensity,
            'parameters': self._parameters,
        }
