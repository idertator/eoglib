from eoglib.models import Channel


class CalibrationError(Exception):

    def __init__(self, reason: str):
        self._reason = reason

    def __str__(self):
        return self._reason
