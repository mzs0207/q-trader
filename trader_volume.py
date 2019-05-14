#!/usr/bin/env python
# coding:utf8
import time
import datetime
import os
import logging
import ccxt
import json
from agent.agent import Agent
from functions import *
from mail_help import send_message

config = None
with open('config.json') as f:
    config = json.load(f)

print config
window_size = 32
agent = Agent(window_size * 10, 'k_data_10')
batch_size = 32
total_profit = 0
agent.inventory = []
exchange = ccxt.bitmex()
exchange.apiKey = config['key']
exchange.secret = config['secret']
trade_log_file = os.path.join(os.path.dirname(__file__), 'trade.log')
logging.basicConfig(
    level=logging.INFO,
    filemode='a',
    filename=trade_log_file,
    format="%(asctime)s %(message)s"
)


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


logging.info("run")


while 1:
    try:
        data, closes = get_bitmex_data()
        state = getState(data, len(data) - 1, window_size + 1)
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
        if action == 1 and len(agent.inventory) < 1:  # buy
            try:
                exchange.create_market_buy_order('BTC/USD', 30)
                agent.inventory.append(closes[-1])
                total_profit -= 30.0 / closes[-1] * 1000.0 * 0.00075
                print "Buy:{0}".format(closes[-1])
            except Exception as e:
                logging.exception(e)

        elif action == 2 and len(agent.inventory) > 0:  # sell
            try:
                exchange.create_market_sell_order("BTC/USD", 30)
                buy_price = agent.inventory.pop(0)
                total_profit += (1.0 / buy_price - 1.0 / closes[-1]) * 30 * 1000
                total_profit -= 30.0 / closes[-1] * 1000.0 * 0.00075
                s = "Close positions.first :buy {0} sell:{1} ".format(buy_price, closes[-1])
                print s
                logging.info(s)
                #send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))

                print "total_profit:{0}".format(total_profit)
                logging.info("total_profit:{0}".format(total_profit))
            except Exception as e:
                logging.exception(e)
    except Exception as e:
        print e.message
        logging.exception(e)

    sleep_count = 300 - int(time.time()) % 300
    print 'sleep count:', sleep_count
    time.sleep(sleep_count + 2)
