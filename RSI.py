#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 14:01:36 2023

@author: Themanwhosoldtheworld
"""

import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

"""
https://pypi.org/project/yfinance/
"""

def RSI(ticker, window = 14, plot = True ):
    stock      = yf.Ticker(ticker)
    history    = stock.history(interval = '1d', period = 'max')
    
    
    history.index =  history.index.tz_localize(None) 
    history       = history[history.index > datetime(2022, 1, 1)]
    
    history['DoD'] = history['Close'].diff()
    DoD = history['DoD'].values
    
    history['Gain'] = np.where(DoD>0, DoD, 0)
    history['Loss'] = np.where(DoD<0, -DoD, 0)
    
    history['AvgGain'] = history['Gain'].rolling(window).mean()
    history['AvgLoss'] = history['Loss'].rolling(window).mean()
    history['RSI'] = 100 * history['AvgGain'] / (history['AvgGain']+history['AvgLoss'])
    
    history['10DayAvg'] = history['Close'].rolling(10).mean()
    history['30DayAvg'] = history['Close'].rolling(30).mean()
    history['90DayAvg'] = history['Close'].rolling(90).mean()

    
    if plot == True:
        
        plt.style.use('fivethirtyeight')           
        plt.rcParams['figure.figsize'] = (20, 20)
    
        #Multiaxis plot
        hist = plt.subplot2grid((10,1), (0,0), rowspan = 4, colspan = 1)
        RSI  = plt.subplot2grid((10,1), (5,0), rowspan = 4, colspan = 1)
    

        hist.plot(history['Close'], linewidth=2)
        hist.set_title(ticker+' Close Price')
    
        RSI.set_title('Relative Strength Index')
        RSI.plot(history['RSI'], color='orange', linewidth=2)
        
        # Show 30 and 70 mark
        RSI.axhline(30, linestyle='--', linewidth=1.5, color='green')
        RSI.axhline(70, linestyle='--', linewidth=1.5, color='red')

        plt.show()
        
        plt.style.use('fivethirtyeight')           
        plt.rcParams['figure.figsize'] = (20, 20)
    
        #Multiaxis plot
        hist = plt.subplot2grid((10,1), (0,0), rowspan = 4, colspan = 1)
        EMA  = plt.subplot2grid((10,1), (5,0), rowspan = 4, colspan = 1)
    

        hist.plot(history['Close'], linewidth=2)
        hist.set_title(ticker+' Close Price')
    
        EMA.set_title('Moving Averages')
        EMA.plot(history['10DayAvg'], color='orange', linewidth=2)
        EMA.plot(history['30DayAvg'], color='blue', linewidth=2)
        EMA.plot(history['90DayAvg'], color='red', linewidth=2)

        plt.show()
    
    
    return [history]

H = RSI('MSFT')[0]
