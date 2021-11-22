import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import abc
import threading

import numpy as np
import pandas as pd
from keras.layers import Dense
from keras.models import Sequential
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


class TradingSystem(abc.ABC):

    def __init__(self, api, symbol, time_frame, system_id, system_label):
        # Connect to api
        # Connect to BrokenPipeError
        # Save fields to class
        self.api = api
        self.symbol = symbol
        self.time_frame = time_frame
        self.system_id = system_id
        self.system_label = system_label
        thread = threading.Thread(target=self.system_loop)
        thread.start()

    @abc.abstractmethod
    def place_buy_order(self):
        pass

    @abc.abstractmethod
    def place_sell_order(self):
        pass

    @abc.abstractmethod
    def system_loop(self):
        pass


class PortfolioManagementSystem(TradingSystem):

    def __init__(self):
        super().__init__()

    def place_buy_order(self):
        pass

    def place_sell_order(self):
        pass

    def system_loop(self):
        pass


# Class to develop your AI portfolio manager
class AIPMDevelopment:

    def __init__(self):
        # Read your data in and split the dependent and independent
        data = pd.read_csv('C:\\Users\\38097\Desktop\\trade\\test.csv')
        X = data['Delta Close']
        y = data.drop(['Delta Close'], axis=1)


        # Train test spit
        X_train, X_test, y_train, y_test = train_test_split(X, y)
        print(f'X_train = \n{X_train}\nX_test = \n{X_test}\ny_train = {y_train}\ny_test = {y_test}')

        # Create the sequential
        network = Sequential()

        # Create the structure of the neural network
        network.add(Dense(1, input_shape=(1,), activation='relu'))
        network.add(Dense(3, activation='relu'))
        network.add(Dense(3, activation='relu'))
        network.add(Dense(3, activation='relu'))
        network.add(Dense(1, activation='relu'))

        # Compile the model
        network.compile(
                      optimizer='rmsprop',
                      loss='binary_crossentropy',
                      metrics=['accuracy']
                      )
        # Train the model
        network.fit(X_train.values, y_train.values, epochs=100)

        # Evaluate the predictions of the model
        y_pred = network.predict(X_test.values)
        y_pred = np.around(y_pred, 0)
        print(classification_report(y_test, y_pred))

        # Save structure to json
        model = network.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model)

        # Save weights to HDF5
        network.save_weights("weights.h5")

AIPMDevelopment()