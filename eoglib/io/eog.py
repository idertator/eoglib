from io import BytesIO
from os.path import join
from zipfile import ZipFile

from numpy import load, savez_compressed
from orjson import OPT_INDENT_2, dumps, loads

from eoglib.models import Channel, Study

from .openeog import load_openeog


def save_eog(filename: str, study: Study):
    with ZipFile(filename, mode='w') as out:
        study_json = study.to_json()

        for index, test in enumerate(study):
            test_path = f'tests/{index:02}'
            test_channels_json = study_json['tests'][index]['channels']

            channels = test_channels_json.keys()
            saved_channels = {}
            for channel in channels:
                data = test_channels_json[channel]
                full_path = f'{test_path}/{Channel(channel).snake_name}.npz'
                saved_channels[channel] = full_path
                buff = BytesIO()
                savez_compressed(buff, data=data)
                out.writestr(full_path, buff.getvalue())

            study_json['tests'][index]['channels'] = saved_channels

        manifest = dumps(study_json, option=OPT_INDENT_2)
        out.writestr('manifest.json', manifest)


def load_eog(filename: str, data_dir: str = None) -> Study:
    study = None

    with ZipFile(filename, mode='r') as inp:
        with inp.open('manifest.json') as manifest_file:
            manifest = loads(manifest_file.read())

        filename = manifest['parameters']['obci_filename']

        study = Study.from_json(manifest)

        if data_dir is None:
            for test in study:
                for channel, path in test._channels.items():
                    with inp.open(path) as channel_file:
                        test[Channel(channel)] = load(channel_file)['data']
        else:
            test_data = load_openeog(
                filename=join(data_dir, filename),
                apply_filter=True
            )

            for test, (times, idxs, h, v, stim) in zip(study, test_data):
                test[Channel.Timestamps] = times
                test[Channel.Time] = idxs
                test[Channel.Horizontal] = h
                test[Channel.Vertical] = v
                test[Channel.Stimulus] = stim

    return study
