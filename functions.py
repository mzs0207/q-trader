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

    mean_total_volume = 0
    last_close = 0
    last_open = 0
    last_low = 0
    last_high = 0
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

            volume = float(arr[7]) / (close_price)
            volume = volume / 1000.0
            #temp_arr.append(mean_volume)
            #print mean_volume
            #print volume
            total_volume = (float(arr[5]) + float(arr[6])) / close_price
            mean_total_volume = mean_total_volume * p + (1 - p) * total_volume
            mean_total_volume = mean_total_volume/(1 - math.pow(p, t))
            temp_arr.append((high_price - low_price)/low_price)
            temp_arr.append((high_price - open_price)/open_price)
            temp_arr.append((low_price - close_price)/close_price)
            temp_arr.append((low_price - open_price)/open_price)
            temp_arr.append((close_price - open_price)/open_price)
            if last_close == 0:
                temp_arr.append(0)
            else:
                temp_arr.append((close_price - last_close)/last_close)
            if last_open == 0:
                temp_arr.append(0)
            else:
                temp_arr.append((open_price - last_open)/last_open)

            if last_low == 0:
                temp_arr.append(0)
            else:
                temp_arr.append((low_price - last_low)/low_price)
            if last_high == 0:
                temp_arr.append(0)
            else:
                temp_arr.append((high_price - low_price)/low_price)

            v = total_volume/mean_total_volume
            temp_arr.append(v)

            money_vec.append(temp_arr)
            last_close = close_price
            last_high = high_price
            last_low = low_price
            last_open = open_price
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
    for i in xrange(n - 1):
        #res.append(sigmoid(block[i + 1] - block[i]))
        #res.append(block[i + 1] - block[i])
        temp_arr = block[i]
        #res.append(temp_arr[0])
        for m in temp_arr:
            res.append(m)

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


