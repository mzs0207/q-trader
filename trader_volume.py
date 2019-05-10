#!/usr/bin/env python
# coding:utf8
import time
import datetime

import ccxt

from agent.agent import Agent
from functions import *
from mail_help import send_message

window_size = 32
agent = Agent(window_size * 10, 'k_data_4h')
batch_size = 32
total_profit = 0
agent.inventory = []
exchange = ccxt.bitmex()
hold = 0
last_price = 0
last_action = -1


def get_bitmex_data():
    global exchange
    k_data_500 = exchange.fetch_ohlcv(symbol='BTC/USD', timeframe='5m', limit=600, params={'reverse': True})
    total_data = []
    closes = []
    mean_total_volume = 0
    last_close = 0
    last_open = 0
    last_low = 0
    last_high = 0
    t = 1
    p = 0.8

    for item in k_data_500:
        close_price = float(item[4])
        open_price = float(item[1])
        high_price = float(item[2])
        low_price = float(item[3])
        total_volume = float(item[5])
        temp_arr = []
        mean_total_volume = mean_total_volume * p + (1 - p) * total_volume
        mean_total_volume = mean_total_volume / (1 - math.pow(p, t))
        temp_arr.append((high_price - low_price) / low_price)
        temp_arr.append((high_price - open_price) / open_price)
        temp_arr.append((low_price - close_price) / close_price)
        temp_arr.append((low_price - open_price) / open_price)
        temp_arr.append((close_price - open_price) / open_price)
        if last_close == 0:
            temp_arr.append(0)
        else:
            temp_arr.append((close_price - last_close) / last_close)
        if last_open == 0:
            temp_arr.append(0)
        else:
            temp_arr.append((open_price - last_open) / last_open)

        if last_low == 0:
            temp_arr.append(0)
        else:
            temp_arr.append((low_price - last_low) / low_price)
        if last_high == 0:
            temp_arr.append(0)
        else:
            temp_arr.append((high_price - low_price) / low_price)

        v = total_volume / mean_total_volume
        temp_arr.append(v)

        total_data.append(temp_arr)
        closes.append(close_price)
        last_close = close_price
        last_high = high_price
        last_low = low_price
        last_open = open_price
        t += 1

    return total_data, closes


while 1:
    try:
        data, closes = get_bitmex_data()
        state = getState(data, len(data) - 1, window_size+1)
        action = agent.act(state)
        print 'action:', action
        op = ''
        if action == 1:
            op = "Buy"
        if action == 2:
            op = "Sell"
        elif action == 0:
            op = "Nothing"
        print "{0} action:{1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), op)
        if action == 1 and action != last_action:  # buy
            if hold == 0:
                hold += 30
                last_price = closes[-1]
                total_profit -= 30.0/closes[-1] * 1000.0 * 0.00075
                s = "Open positions,buy {0}".format(closes[-1])
                print s
                send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))
            # elif hold < 0:
            #     total_profit += (1.0/closes[-1] - 1.0/last_price) * 30 * 1000
            #     hold += 60
            #     total_profit -= 60.0 / closes[-1] * 1000 * 0.00075
            #     reward = max(last_price - closes[-1], 0)
            #     s = "Close and open positions.first :buy:{0} sell:{1}  second: buy:{0}".format(closes[-1], last_price)
            #     print s
            #     send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))
            #
            #     print "total_profit:{0}".format(total_profit)
            #     last_price = closes[-1]
            last_action = action

        elif action == 2 and action != last_action:  # sell
            # if hold == 0:
            #     hold -= 30
            #     last_price = closes[-1]
            #     total_profit -= 30.0 / closes[-1] * 1000.0 * 0.00075
            #     s = "Open positions, sell {0}".format(closes[-1])
            #     print s
            #     send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))
            if hold > 0:
                total_profit += (1.0/last_price - 1.0/closes[-1]) * 30 * 1000
                hold -= 30
                reward = max(closes[-1] - last_price, 0)
                total_profit -= 30.0 / closes[-1] * 1000.0 * 0.00075
                s = "Close positions.first :buy {0} sell:{1} ".format(last_price, closes[-1])
                print s
                send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))

                print "total_profit:{0}".format(total_profit)
                last_price = closes[-1]
            last_action = action
    except Exception as e:
        print e.message

    sleep_count = 300 - int(time.time()) % 300
    print 'sleep count:', sleep_count
    time.sleep(sleep_count + 2)

