#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Themanwhosoldtheworld
"""


import requests
import statistics
import yfinance as yf
import numpy as np
import time

from Strategies import MovingAverageStrategy
from Strategies import PairsTradingStrategy
from Strategies import DeltaHedgingStrategy
from Strategies import RSIStrategy

# replace the API_KEY with your own IEX Cloud API key
api_key = 'API_KEY'

base_url = 'https://sandbox.iexapis.com/v1'

# make a GET request to test the connection
response = requests.get(f'{base_url}/status', params={'token': api_key})

if response.status_code == 200:
    print('Connection successful!')
else:
    print('Connection failed.')

class OrderManager:
    def __init__(self):
        self.orders = []

    def submit_order(self, symbol, qty, side, type, time_in_force):
        payload = {
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,
            'token': api_key
        }
        response = requests.post(f'{base_url}/orders', params=payload)

        if response.status_code == 200:
            self.orders.append(response.json()['id'])
            print(f'Order submitted: {response.json()["id"]}')
        else:
            print('Order failed to submit.')






def main():
    # initialize order manager
    order_manager = OrderManager()

    # initialize strategies
    ma_strategy             = MovingAverageStrategy("AAPL", order_manager, 5, 10)
    pairs_strategy          = PairsTradingStrategy("AAPL", "MSFT", order_manager)
    delta_hedging_strategy  = DeltaHedgingStrategy("AAPL", order_manager)
    rsi_strategy            = RSIStrategy("AAPL", order_manager)

    # run strategies
    for i in range(100):
        ma_strategy.calculate_signals()
        pairs_strategy.calculate_signals()
        delta_hedging_strategy.calculate_signals()
        rsi_strategy.calculate_signals()

        # wait for next iteration
        time.sleep(1)
