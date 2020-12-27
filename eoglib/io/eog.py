from io import BytesIO
from zipfile import ZipFile

from eoglib.models import Study, Channel
from numpy import array, int32, mean, savez_compressed, load
from orjson import dumps, loads, OPT_INDENT_2


def save_eog(filename: str, study: Study):
    with ZipFile(filename, mode='w') as out:
        study_json = self.study.to_json(False)
        out.writestr('manifest.json', manifest)

        for index, test in enumerate(study):
            test_path = f'tests/{index:02}'
            test_channels_json = study_json['tests'][index]['channels'] = {}
            for channel, data in test.channels:
                full_path = f'{test_path}/{channel.snake_name}.npz'
                test_channels_json[channel.value] = full_path
                buff = BytesIO()
                savez_compressed(buff, data=data)
                out.writestr(buff.read())

        manifest = dumps(study_json, option=OPT_INDENT_2)


def load_eog(filename: str) -> Study:
    study = None

    with ZipFile(filename, mode='r') as inp:
        with inp.open('manifest.json') as manifest_file:
            manifest = loads(manifest_file.read())

        study = Study.from_json(manifest)
        for test in study:
            for channel, path in test.channels.items():
                with inp.open(path) as channel_file:
                    test[Channel(channel)] = load(channel_file)['data']

    return study
