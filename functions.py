import math

import numpy as np
import talib


# prints formatted price
def formatPrice(n):
    return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))


# returns the vector containing stock data from a fixed file
def getStockDataVec(key):
    vec = []
    lines = open("data/" + key + ".csv", "r").read().splitlines()

    for line in lines[1:]:
        vec.append(float(line.split(",")[4]))

    return vec


# returns the sigmoid
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# returns an an n-day state representation ending at time t
def getState(data, t, n):
    d = t - n + 1
    block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1]  # pad with t0
    res = []
    for i in xrange(n - 1):
        res.append(sigmoid(block[i + 1] - block[i]))

    return np.array([res])


def get_state_rsi(data, t, n):
    """

    :param data:
    :param t:
    :param n:
    :return:
    """
    item_data = np.array(data[t: t + n])
    v1 = talib.RSI(item_data, timeperiod=20)[-1]
    v2 = talib.RSI(item_data, timeperiod=60)[-1]
    v3 = talib.RSI(item_data, timeperiod=300)[-1]
    # print int(n / 3), int(n / 3 * 2), n - 1
    return np.array([[v1, v2, v3]]) / 100


if __name__ == '__main__':
    data = getStockDataVec('^GSPC')
    print get_state_rsi(data, 0, 31)
    print getState(data, 0, 10)

