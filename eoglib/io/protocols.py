from eoglib.models import Protocol

from orjson import dumps, loads, OPT_INDENT_2


def save_protocol(filename: str, protocol: Protocol):
    with open(filename, 'wt') as f:
        json = dumps(protocol.to_json(template=True), option=OPT_INDENT_2)
        f.write(json)


def load_protocol(filename: str) -> Protocol:
    with open(filename, 'rt') as f:
        json = loads(f.read())
        return Protocol.from_json(json)
