#!/usr/bin/env python
# coding:utf8
import time
import datetime

import ccxt

from agent.agent import Agent
from functions import *
from mail_help import send_message

agent = Agent(3, 'XBTUSD')
batch_size = 32
total_profit = 0
agent.inventory = []
exchange = ccxt.bitmex()
hold = 0
last_price = 0
last_action = -1


def get_bitmex_data():
    global exchange
    k_data_500 = exchange.fetch_ohlcv(symbol='BTC/USD', timeframe='5m', limit=302, params={'reverse': True})
    temp_data = [item[4] for item in k_data_500]
    return temp_data


data = get_bitmex_data()
state = get_state_rsi(data[:-1], 0, 300 + 1)
episode_count = 0
while 1:
    action = agent.act(state)
    print "{0} action:{1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action)
    reward = 0
    if action == 1 and action != last_action:  # buy
        if hold == 0:
            hold += 30
            last_price = data[-1]
            s = "Open positions,buy {0}".format(data[-1])
            print s
            send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))
        elif hold < 0:
            total_profit += (1.0/data[-1] - 1.0/last_price) * 30 * 1000
            hold += 60
            reward = max(last_price - data[-1], 0)
            s = "Close and open positions.first :buy:{0} sell:{1}  second: buy:{0}".format(data[-1], last_price)
            print s
            send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))

            print "total_profit:{0}".format(total_profit)
            last_price = data[-1]
        last_action = action

    elif action == 2 and action != last_action:  # sell
        if hold == 0:
            hold -= 30
            last_price = data[-1]
            s = "Open positions, sell {0}".format(data[-1])
            print s
            send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))
        if hold > 0:
            total_profit += (1.0/last_price - 1.0/data[-1]) * 30 * 1000
            hold -= 60
            reward = max(data[-1] - last_price, 0)
            s = "Close and open positions.first :buy {0} sell:{1}  second: sell {1}".format(last_price, data[-1])
            print s
            send_message(s, "{0} {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))

            print "total_profit:{0}".format(total_profit)
            last_price = data[-1]
        last_action = action

    sleep_count = 300 - int(time.time()) % 300
    print 'sleep count:', sleep_count
    time.sleep(sleep_count + 1)
    data = get_bitmex_data()
    next_state = get_state_rsi(data[:-1], 0, 300 + 1)
    # print 'next_state', next_state
    # print 'state', state
    # print 'action', action
    # print 'reward', reward
    agent.memory.append((state, action, reward, next_state, False))
    state = next_state
    if len(agent.memory) > batch_size:
        agent.expReplay(batch_size)
        episode_count += 1
    if episode_count % 100 == 0:
        agent.model.save("models/{0}_model_ep{1}".format(agent.stock_name, agent.episode))
        if episode_count > 10000 * 100:
            episode_count = 0
