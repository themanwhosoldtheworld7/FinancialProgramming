#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Themanwhosoldtheworld
"""

class MovingAverageStrategy:
    def __init__(self, symbol):
        self.symbol = symbol
        self.short_window = 50
        self.long_window = 200

    def calculate_signals(self):
        # get historical prices for the stock
        response = requests.get(f'{base_url}/stock/{self.symbol}/chart/1y', params={'token': api_key})
        prices = response.json()
        order_manager = OrderManager()

        # calculate the 50-day and 200-day moving averages
        short_ma = sum([float(price['close']) for price in prices[-self.short_window:]]) / self.short_window
        long_ma = sum([float(price['close']) for price in prices[-self.long_window:]]) / self.long_window

        # check if the short moving average crosses above the long moving average
        if short_ma > long_ma:
            order_manager.submit_order(self.symbol, 100, 'buy', 'market', 'gtc')
        # check if the short moving average crosses below the long moving average
        elif short_ma < long_ma:
            order_manager.submit_order(self.symbol, 100, 'sell', 'market', 'gtc')


class PairsTradingStrategy:
    def __init__(self, symbol1, symbol2, order_manager):
        self.symbol1 = symbol1
        self.symbol2 = symbol2
        self.order_manager = OrderManager()
        self.lookback_period = 100
        self.entry_threshold = 2
        self.exit_threshold = 0.5
        self.trade_size = 100

    def calculate_signals(self):
        # get historical prices for both stocks
        response1 = requests.get(f'{base_url}/stock/{self.symbol1}/chart/1y', params={'token': api_key})
        prices1 = response1.json()
        response2 = requests.get(f'{base_url}/stock/{self.symbol2}/chart/1y', params={'token': api_key})
        prices2 = response2.json()

        # calculate the spread between the two stocks
        spread = [float(prices1[i]['close']) - float(prices2[i]['close']) for i in range(len(prices1))]

        # calculate the mean and standard deviation of the spread over the lookback period
        spread_mean = sum(spread[-self.lookback_period:]) / self.lookback_period
        spread_std = statistics.stdev(spread[-self.lookback_period:])

        # calculate the z-score of the current spread
        z_score = (spread[-1] - spread_mean) / spread_std

        # check if the z-score is above the entry threshold and enter a long-short position
        if z_score > self.entry_threshold:
            self.order_manager.submit_order(self.symbol1, self.trade_size, 'buy', 'market', 'gtc')
            self.order_manager.submit_order(self.symbol2, self.trade_size, 'sell', 'market', 'gtc')
        # check if the z-score is below the negative entry threshold and enter a short-long position
        elif z_score < -self.entry_threshold:
            self.order_manager.submit_order(self.symbol1, self.trade_size, 'sell', 'market', 'gtc')
            self.order_manager.submit_order(self.symbol2, self.trade_size, 'buy', 'market', 'gtc')
        # check if the position should be closed based on the exit threshold
        elif abs(z_score) < self.exit_threshold:
            self.order_manager.submit_order(self.symbol1, self.trade_size, 'sell', 'market', 'gtc')
            self.order_manager.submit_order(self.symbol2, self.trade_size, 'buy', 'market', 'gtc')



class DeltaHedgingStrategy:
    def __init__(self, symbol, option_symbol, order_manager):
        self.symbol = symbol
        self.option_symbol = option_symbol
        self.order_manager = order_manager
        self.stock_price = None
        self.option_price = None
        self.delta = None
        self.prev_delta = None

    def calculate_signals(self):
        # get current prices
        self.stock_price = yf.Ticker(self.symbol).history(period="1d")["Close"][0]
        self.option_price = yf.Ticker(self.option_symbol).history(period="1d")["Close"][0]

        # calculate delta
        self.delta = self.get_delta(self.stock_price, self.option_price)

        # calculate delta change
        if self.prev_delta is not None:
            delta_change = self.delta - self.prev_delta
        else:
            delta_change = 0

        # execute orders based on delta change
        if delta_change > 0:
            self.order_manager.buy(self.symbol, abs(delta_change))
            self.order_manager.sell(self.option_symbol, abs(delta_change))
        elif delta_change < 0:
            self.order_manager.sell(self.symbol, abs(delta_change))
            self.order_manager.buy(self.option_symbol, abs(delta_change))

        # save previous delta
        self.prev_delta = self.delta

    def get_delta(self, stock_price, option_price, strike_price=100, risk_free_rate=0.01, time_to_expiry=1):
        d1 = (np.log(stock_price / strike_price) + (risk_free_rate + (statistics.stdev(np.log(yf.Ticker(self.symbol).history(period="1d")["Close"]))) ** 2 / 2) * time_to_expiry) / (statistics.stdev(np.log(yf.Ticker(self.symbol).history(period="1d")["Close"])) * np.sqrt(time_to_expiry))
        delta = np.exp(-1 * risk_free_rate * time_to_expiry) * statistics.NormalDist().cdf(d1)
        return delta


class RSIStrategy:
    def __init__(self, symbol, order_manager, window_size=14, buy_threshold=30, sell_threshold=70):
        self.symbol = symbol
        self.order_manager = order_manager
        self.window_size = window_size
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.prices = []
        self.ups = []
        self.downs = []
        self.avg_up = None
        self.avg_down = None
        self.prev_rsi = None

    def calculate_signals(self):
        # get current price
        price = yf.Ticker(self.symbol).history(period="1d")["Close"][0]
        self.prices.append(price)

        # calculate price changes
        if len(self.prices) > 1:
            change = price - self.prices[-2]
            if change >= 0:
                self.ups.append(change)
                self.downs.append(0)
            else:
                self.downs.append(abs(change))
                self.ups.append(0)

            # calculate average up/down
            if len(self.ups) == self.window_size:
                self.avg_up = sum(self.ups) / self.window_size
                self.avg_down = sum(self.downs) / self.window_size
                self.ups.pop(0)
                self.downs.pop(0)

                # calculate RSI
                if self.avg_down == 0:
                    rsi = 100
                else:
                    rs = self.avg_up / self.avg_down
                    rsi = 100 - (100 / (1 + rs))

                # execute orders based on RSI
                if self.prev_rsi is not None:
                    if rsi < self.buy_threshold and self.prev_rsi >= self.buy_threshold:
                        self.order_manager.buy(self.symbol, 1)
                    elif rsi > self.sell_threshold and self.prev_rsi <= self.sell_threshold:
                        self.order_manager.sell(self.symbol, 1)

                # save previous RSI
                self.prev_rsi = rsi
