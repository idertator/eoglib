from numpy import array, float32

from eoglib.models import (Board, Channel, Recorder, SaccadicStimulus,
                           SampleRate, Stimulus, StimulusCategory,
                           StimulusOrientation, Study, Test)


def load_otoscreen(filename: str) -> Study:
    study = Study(
        recorder=Recorder(
            board=Board.OtoScreen,
            sample_rate=SampleRate.SR200
        )
    )

    current_angle = 0
    current_channel = None
    current_channels = {}
    current_duration = 0.0
    current_data = []
    current_category = None
    current_category_text = None
    current_random = False

    channels_dict = {
        'Horizontal': Channel.Horizontal,
        'Vertical': Channel.Vertical,
        'Vertikal': Channel.Vertical,
    }

    tests_dict = {
        'Calibration hor': StimulusCategory.Saccadic,
        'Calibration ver': StimulusCategory.Saccadic,
        'Saccade Test': StimulusCategory.Saccadic,
        'Spontaneous Nystagmus': StimulusCategory.Unknown,
        'Pursuit Test': StimulusCategory.Pursuit,
        'Gaze Test': StimulusCategory.Unknown,
        'Optokinetic Test': StimulusCategory.Unknown,
        'Optocinetic Test': StimulusCategory.Unknown,
        'Antisacada 1': StimulusCategory.Antisaccadic,
        'Antisacada 2': StimulusCategory.Antisaccadic,
    }

    tests_orientation = {
        'Calibration hor': StimulusOrientation.Horizontal,
        'Calibration ver': StimulusOrientation.Vertical,
        'Saccade Test': StimulusOrientation.Both,
        'Spontaneous Nystagmus': StimulusOrientation.Unknown,
        'Pursuit Test': StimulusOrientation.Both,
        'Gaze Test': StimulusOrientation.Unknown,
        'Optokinetic Test': StimulusOrientation.Unknown,
        'Optocinetic Test': StimulusOrientation.Unknown,
        'Antisacada 1': StimulusOrientation.Both,
        'Antisacada 2': StimulusOrientation.Both,
    }

    def add_test(current_channels, current_data, current_random):
        if current_category == StimulusCategory.Saccadic:
            stimulus = SaccadicStimulus(
                calibration='Calibration' in current_category_text,
                angle=current_angle,
                orientation=tests_orientation[current_category_text]
            )
        else:
            stimulus = Stimulus(
                calibration='Calibration' in current_category_text
            )

        if current_data:
            current_channels[Channel.Stimulus] = array(current_data, dtype=float32)

        study.append(
            Test(
                stimulus=stimulus,
                channels=current_channels,
                study=study,
                length=current_duration / 1000.0,
                random=current_random
            )
        )

    with open(filename, 'r', encoding='latin_1') as ifile:
        while True:
            line = ifile.readline()

            if not line:
                break

            if line.startswith('Sequenz'):
                if current_data and current_category_text in {
                    'Calibration hor',
                    'Saccade Test',
                }:
                    add_test(current_channels, current_data, current_random)
                    current_data = []
                    current_channels = {}
                    current_random = False

                    current_angle = 0
                    current_channel = None
                    current_duration = 0.0

                current_category_text = line.split('\t')[1]
                current_category = tests_dict[current_category_text]

            if line.startswith('OKN angle'):
                current_angle = int(float(line.split('\t')[1]))

            if line.startswith('Channel'):
                if current_channel is not None:
                    current_channels[current_channel] = array(current_data, dtype=float32)
                    current_data = []
                current_channel = channels_dict[line.split('\t')[1]]

            if line.startswith('Zeit') and current_channel == 4:
                current_duration += float(line.split('\t')[1])

            if line.startswith('Points'):
                count = int(line.split('\t')[1])
                for i in range(count):
                    current_data.append(float32(ifile.readline().split('\t')[1]))

            if line.startswith('Add.') and 'Random' in line:
                current_random = True

        if current_data and current_category_text in {
            'Calibration hor',
            'Saccade Test',
        }:
            add_test(current_channels, current_data, current_random)

        return study

    return None
