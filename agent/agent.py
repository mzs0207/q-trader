from keras.models import Sequential
import random
from collections import deque

from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense
from keras.optimizers import Adam
import numpy as np
import os


class Agent:
    def __init__(self, state_size, stock_name, is_eval=False, model_name=""):
        self.state_size = state_size  # normalized previous days
        self.action_size = 3  # sit, buy, sell
        self.memory = deque(maxlen=1000)
        self.inventory = []
        self.model_name = model_name
        self.is_eval = is_eval
        self.stock_name = stock_name

        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.episode = 0

        # self.model = load_model("models/" + model_name) if is_eval else self._model()
        self.model = self.load_existing_model()

    def _model(self):
        model = Sequential()
        model.add(Dense(units=64, input_dim=self.state_size, activation="relu"))
        model.add(Dense(units=32, activation="relu"))
        model.add(Dense(units=8, activation="relu"))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=0.001))

        return model

    def act(self, state):
        if not self.is_eval and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        options = self.model.predict(state)
        return np.argmax(options[0])

    def expReplay(self, batch_size):
        mini_batch = []
        l = len(self.memory)
        for i in xrange(l - batch_size + 1, l):
            mini_batch.append(self.memory[i])

        for state, action, reward, next_state, done in mini_batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])

            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load_existing_model(self):

        if not os.path.exists('models'):
            raise Exception("models not exists,please create")
        models = os.listdir('models')
        models = [name for name in models if self.stock_name in name]
        if len(models) == 0:
            print('new model')
            return self._model()
        name_pre_length = len(self.stock_name) + 9
        for model_name in models:
            num = int(model_name[name_pre_length:])
            if num > self.episode:
                self.episode = num
        print('load {0}_model_ep{1}'.format(self.stock_name, self.episode))
        return load_model('models/{0}_model_ep{1}'.format(self.stock_name, self.episode))


