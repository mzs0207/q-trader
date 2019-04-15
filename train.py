import sys

from agent.agent import Agent
from functions import *

if len(sys.argv) != 4:
    print "Usage: python train.py [stock] [window] [episodes]"
    exit()

stock_name, window_size, episode_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

agent = Agent(3, stock_name)
data = getStockDataVec(stock_name)
episode_count -= agent.episode
l = len(data) - 1
batch_size = 32

for e in xrange(episode_count + 1):
    print "Episode " + str(e) + "/" + str(episode_count)
    state = get_state_rsi(data, 0, window_size + 1)

    total_profit = 0
    agent.inventory = []

    for t in xrange(window_size, l):
        action = agent.act(state)

        # sit
        next_state = get_state_rsi(data, t + 1, window_size + 1)
        reward = 0

        if action == 1:  # buy
            agent.inventory.append(data[t])
            print "Buy: " + formatPrice(data[t])

        elif action == 2 and len(agent.inventory) > 0:  # sell
            bought_price = agent.inventory.pop(0)
            reward = max(data[t] - bought_price, 0)
            total_profit += data[t] - bought_price
            print "Sell: " + formatPrice(data[t]) + " | Profit: " + formatPrice(data[t] - bought_price)

        done = True if t == l - 1 else False
        agent.memory.append((state, action, reward, next_state, done))
        state = next_state

        if done:
            for bought_price in agent.inventory:
                total_profit += data[t] - bought_price
            agent.inventory = []
            print "--------------------------------"
            print "Total Profit: " + formatPrice(total_profit)
            print "--------------------------------"
            with open('Profit.txt', 'a') as f:
                f.write("{0}\n".format(total_profit))

        if len(agent.memory) > batch_size:
            agent.expReplay(batch_size)

    if e % 1 == 0:
        agent.model.save("models/{0}_model_ep{1}".format(stock_name, e + agent.episode))
