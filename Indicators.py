from statistics import stdev, mean
from scipy.stats import pearsonr
import numpy as np


def LINEARREG(close, timeperiod=26):
    reg = [np.nan for w in range(0, timeperiod-1)]
    for index in range(len(close) - timeperiod + 1):
        x = [w for w in range(index, timeperiod + index)]
        y = close[index: timeperiod + index]

        x_avg = mean(x)
        y_avg = mean(y)
        x_stdev = stdev(x)
        y_stdev = stdev(y)
        corr = pearsonr(x, y)[0]

        slope = corr * (y_stdev / x_stdev)
        inter = y_avg - (slope * x_avg)

        reg.append((x[-1] * slope) + inter)

    return reg


def STREAM_LINEARREG(close, timeperiod=26):

    x = [x for x in range(len(close) - timeperiod, len(close))]

    y = close[len(close) - timeperiod: len(close)]

    x_avg = mean(x)
    y_avg = mean(y)
    x_stdev = stdev(x)
    y_stdev = stdev(y)
    corr = pearsonr(x, y)[0]

    slope = corr * (y_stdev / x_stdev)
    inter = y_avg - (slope * x_avg)

    reg = (x[-1] * slope) + inter

    return reg
