import math

import numpy as np
import talib


# prints formatted price
def formatPrice(n):
    return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))


# returns the vector containing stock data from a fixed file
def getStockDataVec(key):
    price_vec = []
    money_vec = []
    lines = open("data/" + key + ".csv", "r").read().splitlines()

    last_close = 0
    t = 1
    p = 0.8
    for line in lines[1:]:
        arr = line.split(",")
        total_money = (float(arr[5]) + float(arr[6]))
        temp_arr = []
        if total_money > 0:

            close_price = float(arr[4])
            open_price = float(arr[1])
            high_price = float(arr[2])
            low_price = float(arr[3])
            price_vec.append(close_price)

            total_volume = (float(arr[5]) + float(arr[6])) / close_price
            temp_arr.append((high_price - low_price)/low_price)
            temp_arr.append((high_price - open_price)/open_price)
            temp_arr.append((high_price - close_price)/close_price)
            temp_arr.append((low_price - close_price)/close_price)
            temp_arr.append((low_price - open_price)/open_price)
            temp_arr.append((close_price - open_price)/open_price)
            temp_arr.append(total_volume)
            money_vec.append(temp_arr)

            t += 1

    return price_vec, money_vec


# returns the sigmoid
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# returns an an n-day state representation ending at time t
def getState(data, t, n):
    d = t - n + 1
    block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1]  # pad with t0
    res = []
    total_arr = []
    for i in range(len(block[0])):
        total_arr.append(sum([abs(m[i]) for m in block]))
    for i in xrange(n - 1):
        temp_arr = block[i]
        for j in range(len(temp_arr)):
            if total_arr[j] == 0:
                res.append(0)
            else:
                res.append(temp_arr[j] / total_arr[j])
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
    data = getStockDataVec('k_data_10')[1]
    # for item in data:
    #     print item
    #     print


