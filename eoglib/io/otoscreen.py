from eoglib.models import Study, Channel


def load_otoscreen(filename: str) -> Study:
    study = Study()

    current_angle = 0.0
    current_channel = 0
    current_channels = {}
    current_duration = 0.0
    current_data = []
    current_category = None
    current_random = False

    channels = 0

    channels_dict = {
        'Horizontal': ChannelType.Horizontal,
        'Vertical': ChannelType.Vertical,
        'Vertikal': ChannelType.Vertical,
    }

    tests_dict = {
        'Calibration hor': TestType.HorizontalCalibration,
        'Calibration ver': TestType.VerticalCalibration,
        'Saccade Test': TestType.Saccadic,
        'Spontaneous Nystagmus': TestType.Unknown,
        'Pursuit Test': TestType.SmoothPursuit,
        'Gaze Test': TestType.Unknown,
        'Optokinetic Test': TestType.Unknown,
        'Optocinetic Test': TestType.Unknown,
        'Antisacada 1': TestType.Antisaccadic,
        'Antisacada 2': TestType.Antisaccadic,
    }

    with open(file_path, 'r', encoding='latin_1') as ifile:
        while True:
            line = ifile.readline()

            if not line:
                break

            if line.startswith('Sequenz'):
                if current_data:
                    if current_channel != 0:
                        if current_channel == 1:
                            current_channels[ChannelType.Horizontal] = array(current_data, dtype=float64)
                        elif current_channel == 2:
                            current_channels[ChannelType.Vertical] = array(current_data, dtype=float64)
                        elif current_channel == 4:
                            current_channels[ChannelType.Stimulus] = array(current_data, dtype=float64) / 10.0
                        current_data = []

                    samples_count = 0
                    if ChannelType.Horizontal in current_channels:
                        samples_count += len(current_channels[ChannelType.Horizontal])
                    if ChannelType.Vertical in current_channels:
                        samples_count += len(current_channels[ChannelType.Vertical])
                    if ChannelType.Stimulus in current_channels:
                        samples_count += len(current_channels[ChannelType.Stimulus])

                    if samples_count > 0:
                        study.add_test(Test(
                            category=current_category,
                            channels=current_channels,
                            angle=current_angle,
                            length=current_duration,
                            random=current_random,
                            parent=study
                        ))
                        current_channels = {}
                        current_random = False

                    current_angle = 0
                    current_channel = 0
                    current_duration = 0.0

                    channels = 0

                current_category = tests_dict[line.split('\t')[1]]
                if current_category == TestType.VerticalCalibration:
                    channels = 1

            if line.startswith('OKN angle'):
                current_angle = float(line.split('\t')[1])

            if line.startswith('Channel'):
                if current_channel != 0:
                    if current_channel == 1:
                        current_channels[ChannelType.Horizontal] = array(current_data, dtype=float64)
                    elif current_channel == 2:
                        current_channels[ChannelType.Vertical] = array(current_data, dtype=float64)
                    elif current_channel == 4:
                        current_channels[ChannelType.Stimulus] = array(current_data, dtype=float64) / 10.0
                    current_data = []

                current_channel_flag = channels_dict[line.split('\t')[1]]

                if channels & current_channel_flag == 0:
                    current_channel = current_channel_flag
                    channels |= current_channel_flag
                else:
                    current_channel = 4
                    channels |= 4

            if line.startswith('Zeit') and current_channel == 4:
                current_duration += float(line.split('\t')[1])

            if line.startswith('Points'):
                count = int(line.split('\t')[1])
                for i in range(count):
                    current_data.append(float64(ifile.readline().split('\t')[1]))

            if line.startswith('Add.') and 'Random' in line:
                current_random = True

        if current_data is not None:
            if current_channel != 0:
                if current_channel == 1:
                    current_channels[ChannelType.Horizontal] = array(current_data, dtype=float64)
                elif current_channel == 2:
                    current_channels[ChannelType.Vertical] = array(current_data, dtype=float64)
                elif current_channel == 4:
                    current_channels[ChannelType.Stimulus] = array(current_data, dtype=float64)

            samples_count = 0
            if ChannelType.Horizontal in current_channels:
                samples_count += len(current_channels[ChannelType.Horizontal])
            if ChannelType.Vertical in current_channels:
                samples_count += len(current_channels[ChannelType.Vertical])
            if ChannelType.Stimulus in current_channels:
                samples_count += len(current_channels[ChannelType.Stimulus])

            if samples_count > 0:
                study.add_test(Test(
                    category=current_category,
                    channels=current_channels,
                    angle=current_angle,
                    length=current_duration,
                    random=current_random,
                    parent=study
                ))

        return study
    pass
