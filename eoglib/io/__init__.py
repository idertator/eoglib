from .diff import load_diff
from .eog import save_eog, load_eog
from .openbci import load_openbci
from .protocols import load_protocol, save_protocol


__all__ = [
    'load_diff',
    'save_eog',
    'load_eog',
    'load_openbci',
    'load_protocol',
    'save_protocol',
]
