#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 17:16:39 2023

@author: Themanwhosoldtheworld
"""


import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

"""
https://pypi.org/project/yfinance/
"""

class TechnicalIndicators:
    StockData = None
    EndDate = datetime.now()
    StartDate = datetime(2022,1,1)
    
    def SetDateWindow(self, **kwargs):
        try:
            self.StartDate = datetime.strptime(kwargs['start'], '%Y%m%d')
        except:
            self.StartDate = datetime(2022,1,1)
        try:
            self.EndDate = datetime.strptime(kwargs['end'], '%Y%m%d')
        except:
            EndDate = datetime.now()
        return
    
    def getStockData(self, ticker):
        self.ticker = ticker
        self.StockData = yf.download(tickers=ticker, start=self.StartDate, end=self.EndDate, interval="1d")
        return
        
    def CalculateRSI(self, window = 14):
        self.StockData.index        =  self.StockData.index.tz_localize(None) 
        self.StockData              =  self.StockData[self.StockData.index > self.StartDate]
        
        self.StockData['DoD']       = self.StockData['Close'].diff()
        DoD                         = self.StockData['DoD'].values
        
        self.StockData['Gain']      = np.where(DoD>0, DoD, 0)
        self.StockData['Loss']      = np.where(DoD<0, -DoD, 0)
        
        self.StockData['AvgGain']   = self.StockData['Gain'].rolling(window).mean()
        self.StockData['AvgLoss']   = self.StockData['Loss'].rolling(window).mean()
        self.StockData['RSI']       = 100 * self.StockData['AvgGain'] / (self.StockData['AvgGain']+self.StockData['AvgLoss'])        
        
        return
    
    def CalculateMA(self, short = 10, long = 30, other = None):
        self.StockData['ShortMA']   = self.StockData['Close'].rolling(short).mean()
        self.StockData['LongMA']    = self.StockData['Close'].rolling(long).mean()
        try:            
            self.StockData['OtherMA'] = self.StockData['Close'].rolling(other).mean()
        except:
            return
        return
    
    def CalculateFibonacciLevels(self, lookback):
        fib                         = self.StockData.iloc[::-1]
        fib                         = fib.head(lookback)
        self.max_level              = fib['Close'].max()
        self.min_level              = fib['Close'].min()
        levels                      = [.76, .68, .5, .32, .26]
        
        self.support     = []
        diff = self.max_level - self.min_level
        
        for level in levels:
            self.support.append(self.min_level + level*diff)
        return

    def PlotCharts(self):
        plt.style.use('fivethirtyeight')           
        plt.rcParams['figure.figsize'] = (20, 20)
    
        #Multiaxis plot
        price   = plt.subplot2grid((10,1), (0,0), rowspan = 4, colspan = 1)
        rsi     = plt.subplot2grid((10,1), (5,0), rowspan = 4, colspan = 1)
        
            

        price.plot(self.StockData['Close'], linewidth=2)
        price.plot(self.StockData['ShortMA'], linewidth = 2, color = 'red')
        price.plot(self.StockData['LongMA'], linewidth = 2, color = 'purple')
        price.plot(self.StockData['OtherMA'], linewidth = 2, color = 'purple')
        price.set_title(self.ticker+' Close Price')
    
        rsi.set_title('Relative Strength Index')
        rsi.plot(self.StockData['RSI'], color='orange', linewidth=2)
        
        for support in self.support:
            price.axhline(support, linestyle = '--', linewidth = 2.0, color = 'green')
        
        # Show 30 and 70 mark
        rsi.axhline(30, linestyle='--', linewidth=1.5, color='green')
        rsi.axhline(70, linestyle='--', linewidth=1.5, color='red')

        #plt.show()
        self.plot = plt
        
        pass


A = TechnicalIndicators()
A.SetDateWindow()
A.getStockData('AAPL')
A.CalculateRSI(14)
A.CalculateMA(30, 90, 60)
A.CalculateFibonacciLevels(120)
A.PlotCharts()
A.plot.show()



