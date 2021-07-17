from math import e

from numpy import arange, argmax, ndarray, vectorize
from scipy.optimize import minimize

from eoglib.models import Annotation


def siggauss2(x, a, b, c, a1, b1, c1, a2, b2, c2, d):
    sig = a * (1 / (e ** ((b - x) / c) + 1))
    g1 = a1 * e ** ((-(b1 - x)**2) / c1**2)
    g2 = a2 * e ** ((-(b2 - x)**2) / c2**2)
    return sig + g1 + g2 + d


def d_siggauss2(x, a, b, c, a1, b1, c1, a2, b2, c2):
    d_sig = (a * (e**((b - x) / c))) / (c * (e**((b - x) / c) + 1)**2)
    d_g1 = (2 * a1 * (b1 - x) * e**(-((b1 - x)**2) / (c1**2))) / (c1**2)
    d_g2 = (2 * a2 * (b2 - x) * e**(-((b2 - x)**2) / (c2**2))) / (c2**2)
    return d_sig + d_g1 + d_g2


v_siggauss2 = vectorize(
    siggauss2,
    excluded=['a', 'b', 'c', 'a1', 'b1', 'c1', 'a2', 'b2', 'c2', 'd']
)


vd_siggauss2 = vectorize(
    d_siggauss2,
    excluded=['a', 'b', 'c', 'a1', 'b1', 'c1', 'a2', 'b2', 'c2', 'd']
)


def compute_saccadic_biomarkers(
    s: Annotation,
    y: ndarray,
    step: float,
    velocity_threshold: float = 30
) -> Annotation:
    delta = int((s.offset - s.onset) // 2)
    left, right = s.onset - delta, s.offset + delta

    Y = y[left:right]
    X = arange(len(Y)) * step

    p0 = [
        abs(y[s.offset] - y[s.onset]),     # a
        X[len(X) // 2],                    # b,
        Y[len(X) // 2],                    # c,
        0.1,                               # a1,
        X[delta],                          # b1,
        0.001,                             # c1,
        0.1,                               # a2,
        X[len(X) - delta],                 # b2,
        0.001,                             # c2,
        abs(y[s.offset] - y[s.onset]) / 2  # d
    ]

    def rmse(params) -> float:
        fitted = v_siggauss2(X, *params)
        return sum((fitted - Y) ** 2) / len(Y)

    results = minimize(rmse, x0=p0, method='Powell')
    params = results.x

    s['fit_error'] = results.fun

    Yfit = v_siggauss2(X, *params)
    Vfit = abs(vd_siggauss2(X, *params[:-1]))

    s['peak_velocity'] = max(Vfit)
    max_velocity_index = int(argmax(Vfit))
    onset = max_velocity_index
    while onset > 0 and Vfit[onset] > velocity_threshold:
        onset -= 1
    offset = max_velocity_index
    while offset < len(X) - 1 and Vfit[offset] > velocity_threshold:
        offset += 1

    s.onset = onset + left
    s.offset = offset + left

    s['latency'] = (s.onset - s['transition']) * step
    s['duration'] = (s.offset - s.onset) * step

    s['amplitude'] = abs(Yfit[offset] - Yfit[onset])
    s['deviation'] = s['amplitude'] / s['angle']

    return s
