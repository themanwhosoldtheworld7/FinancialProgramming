#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 14:11:34 2023

@author: Themanwhosoldtheworld
"""

import math
import numpy as np
import matplotlib.pyplot as plt

def black_scholes(call_put_flag, S, K, T, r, v):
    d1 = (math.log(S / K) + (r + 0.5 * v ** 2) * T) / (v * math.sqrt(T))
    d2 = d1 - v * math.sqrt(T)

    if call_put_flag == 'c':
        price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    elif call_put_flag == 'p':
        price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)

    return price

def norm_cdf(x):
    """Cumulative distribution function for the standard normal distribution."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

# Input parameters
S = 100    # current stock price
T = 1      # time to expiration (in years)
r = 0.05   # risk-free interest rate
v = 0.2    # annualized volatility
strikes = np.arange(80, 120, 5)    # list of strike prices

# Calculate option prices and plot results
call_prices = [black_scholes('c', S, K, T, r, v) for K in strikes]
put_prices = [black_scholes('p', S, K, T, r, v) for K in strikes]

fig, ax = plt.subplots()
ax.plot(strikes, call_prices, label='Call')
ax.plot(strikes, put_prices, label='Put')
ax.legend()
ax.set_xlabel('Strike Price')
ax.set_ylabel('Option Price')
ax.set_title('Black-Scholes Option Prices')
plt.show()
