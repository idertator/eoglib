from numpy import ndarray
from scipy.signal import butter, filtfilt, iirnotch, lfilter


_NOTCH = {
    50: {
        250: iirnotch(50, 30, 250),
        1000: iirnotch(50, 30, 1000),
    },
    60: {
        250: iirnotch(60, 30, 250),
        1000: iirnotch(60, 30, 1000),
    }
}


def notch_filter(data: ndarray, sampling_rate: int, cut_frequency: int) -> ndarray:
    b, a = _NOTCH[cut_frequency][sampling_rate]
    return lfilter(b, a, data)


def butter_filter(data: ndarray, sampling_rate: int, cut_frequency: int) -> ndarray:
    nyq = 0.5 * sampling_rate
    normal_cutoff = cut_frequency / nyq
    b, a = butter(2, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

