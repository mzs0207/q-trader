import sys

from agent.agent import Agent
from functions import *

if len(sys.argv) != 4:
    print "Usage: python train.py [stock] [window] [episodes]"
    exit()

stock_name, window_size, episode_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

agent = Agent(window_size * 7, stock_name)
price_data, money_data = getStockDataVec(stock_name)
episode_count -= agent.episode
l = len(price_data) - 1
batch_size = 32

total_profits = []

for e in xrange(episode_count + 1):
    print "Episode " + str(e) + "/" + str(episode_count)
    state = getState(money_data, 0, window_size + 1)

    total_profit = 0
    agent.inventory = []

    for t in xrange(window_size, l):
        action = agent.act(state)

        # sit
        next_state = getState(money_data, t + 1, window_size + 1)
        reward = 0

        if action == 1 and len(agent.inventory) < 1:  # buy
            agent.inventory.append(price_data[t])
            print "Buy: " + formatPrice(price_data[t])

        elif action == 2 and len(agent.inventory) > 0:  # sell
            bought_price = agent.inventory.pop(0)
            #reward = max(price_data[t] - bought_price, 0)
            pct = (price_data[t] - bought_price) / bought_price * 100
            reward = max(pct, 0)
            #reward = pct
            #total_profit += price_data[t] - bought_price
            this_profit = 100 * (price_data[t] - bought_price) / bought_price
            total_profit = total_profit + this_profit
            print "Sell: " + formatPrice(price_data[t]) + " | Profit: " + formatPrice(this_profit) + " | Total Profit: " + formatPrice(total_profit)
            total_profits.append(str(total_profit))

        done = True if t == l - 1 else False

        agent.memory.append((state, action, reward, next_state, done))
        state = next_state

        if done:
            for bought_price in agent.inventory:
                #total_profit += price_data[t] - bought_price
                this_profit = 100 * (price_data[t] - bought_price) / bought_price
                total_profit = total_profit + this_profit
            agent.inventory = []
            print "--------------------------------"
            print "Total Profit: " + formatPrice(total_profit)
            print "--------------------------------"
            with open('Profit.txt', 'a') as f:
                f.write("{0}\n".format(total_profit))
            with open('Profit_history.txt','a') as f:
                f.write("{0},{1}\n".format(agent.episode + e, ','.join(total_profits)))

        if len(agent.memory) > batch_size:
            agent.expReplay(batch_size)

    if e % 1 == 0:
        agent.model.save("models/{0}_model_ep{1}".format(stock_name, e + agent.episode))
