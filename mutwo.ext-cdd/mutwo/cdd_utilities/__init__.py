import datetime

import numpy as np

__all__ = ("duration_in_seconds_to_readable_duration", "reject_outliers")


def duration_in_seconds_to_readable_duration(duration_in_seconds: float) -> str:
    _, minutes, seconds = str(datetime.timedelta(seconds=duration_in_seconds)).split(
        ":"
    )
    return f"{minutes}'{seconds[:2]}"


# Please see
# https://stackoverflow.com/questions/11686720/is-there-a-numpy-builtin-to-reject-outliers-from-a-list
# This is an adapted version which replaces high outliers by allowed maxima
# and low outliers by allowed minima.
def reject_outliers(data: np.ndarray, m: float = 2.0) -> np.ndarray:
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0.0
    cleaned_data = data[s < m]
    minima = np.min(cleaned_data)
    maxima = np.max(cleaned_data)
    new_data = np.copy(data)
    new_data[new_data < minima] = minima
    new_data[new_data > maxima] = maxima
    return new_data
