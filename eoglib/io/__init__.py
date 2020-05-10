from .diff_matlab import DiffMatlabFormat

from eoglib.models import Record


def load(path: str) -> Record:
    if path.lower().endswith('.mat'):
        return DiffMatlabFormat.load(path)
    raise AttributeError('File format is not supported')

