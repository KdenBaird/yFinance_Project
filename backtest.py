from backtesting import Backtest, Strategy
import pandas as pd
import backtesting 
# GPT suggested this to fix error
from bokeh.models import DatetimeTickFormatter
# from main import bullish_fvgs, bearish_fvgs
# This library works by the indicator is used for the close, and if there's a buy it'll buy @ the next candle's open same w/ sell
"""
2. Check if Already in a Position
To ensure that you don't enter a new position if you're already in one, you can use the self.position attribute, which holds information
 about the current position. This attribute allows you to check whether you are long, short, or flat (no position).

self.position.size > 0: You're in a long position.
self.position.size < 0: You're in a short position.
self.position.size == 0: You're flat (no position).

3. Close Positions
To close an existing position, you can use the self.position.close() method. This will close the current position at the next open price.
"""

class fiveMinFVG(Strategy):
    bullish_fvgs = []
    bearish_fvgs = []

    # I might need to add bullish fvgs and bearish fvgs in this init function? Ask alec or research so u understand
    def init(self):
        self.last_trade_date = None  # Initialize to store the date of the last trade

        # Define the trading window (9:50 AM to 11:10 AM)
        self.start_time = pd.Timestamp("09:50:00").time()
        self.end_time = pd.Timestamp("10:20:00").time()
        
    # This next function goes through each candle in the df one by one and evaluates the criteria, and decides whether it 
    # wants to buy or sell on the next candle.
  
    def next(self):
        # TODO: READ DOCUMENTATION IF YOU'RE NOT FAMILIAR W A LIBRARY. e.g. the data is not a df, it's a customized structure. use ctrl click to understand
        # more information about it:
        """
        Custom Data Structure: The data attribute is not a Pandas DataFrame but a custom structure that serves optimized NumPy arrays for performance reasons.
        Access to Full Data: During the init phase, the data is available in its entirety. However, within the next method, you only have access to the data up
        to the current point in the backtest.
        Convenience Accessors: You can get Pandas Series (with .s) or the entire DataFrame (with .df) for the data if you need more advanced data manipulation.
        """
        # The bug im getting is not a tz issue current date time and fvgs time zone align. 

        df = self.data.df
            
        current_time = self.data.index[-1].time()  # Get the time of the current candle
        current_close = self.data.Close[-1]  # Current candle close price
        current_datetime = self.data.index[-1]  # Ensure this is correct; adjusted as needed
        current_open = self.data.Open[-1]
        prev_close = self.data.Close[-2]
        prev_open = self.data.Open[-2]
        current_date = current_datetime.date()

        # Define TP and SL
        long_tp_price = current_close + 40.00
        long_sl_price = current_close - 20.00

        short_tp_price = current_close - 40.00
        short_sl_price = current_close + 20.00
        

        if current_date != self.last_trade_date:
           # Iterate through Bearish FVGs
            for fvg in self.bearish_fvgs[:]:
                if current_datetime >= fvg['Datetime'] and current_datetime.date() == fvg['Datetime'].date():
                    # Filter relevant data from FVG creation time to current candle 
                    relevant_data = df.loc[fvg['Datetime']:pd.Timestamp(f"{current_date} {self.start_time}").tz_localize('America/New_York'), 'Close']
                    
                    # Check if any closing price before 9:50 AM is above the first candle low
                    invalidated = (relevant_data > fvg['First Candle Low']).any()
                    
                    if invalidated:
                        print(f"Bearish FVG invalidated at {current_datetime} for FVG created at {fvg['Datetime']}")
                        self.bearish_fvgs.remove(fvg)

            # Iterate through Bullish FVGs
            for fvg in self.bullish_fvgs[:]:
                if current_datetime >= fvg['Datetime'] and current_datetime.date() == fvg['Datetime'].date():
                    # Filter relevant data from FVG creation time to 9:50 AM
                    relevant_data = df.loc[fvg['Datetime']:pd.Timestamp(f"{current_date} {self.start_time}").tz_localize('America/New_York'), 'Close']
                    
                    # Check if any closing price before 9:50 AM is below the first candle high
                    invalidated = (relevant_data < fvg['First Candle High']).any()
        
                    if invalidated:
                        print(f"Bullish FVG invalidated at {current_datetime} for FVG created at {fvg['Datetime']}")
                        self.bullish_fvgs.remove(fvg)

            """
            TODO: 
            - we're placing sell orders on up close candles, and buy orders, on downclose candles if it's getting it's signal from a fvg before trading window I THINK THIS IS DONE
            - two signals are being placed (buy and sell) on the same candle open. I THINK THIS IS DONE. 
            - Ensure that two trades are not being placed at the same time. this is done
            - Ensure there is a max num of trades per day. either one or two. THIS IS DONE
            - The logic for invalidating candles is not fully correct yet. e.g. if candle closes above bearish fvg before trading window, sometimes it won't invalidate. 
            - ^^^ This thing, in the if invalidated, we're comparing datetime, and candlestick highs and lows? we should be comparing the close... 
            - Invalidating all fvgs even within trading window right now. 
            - IF A CANDLE HITS TP AND SL IN SAME CANDLE, I BELIEVE IT ASSUMES YOU GOT STOPPED OUT. 
        """ 
            # Ensure we're within the allowed trading window before placing trades
            if self.start_time <= current_time <= self.end_time:
                if not self.position:
                    # Check for a valid Bearish FVG trade signal
                    for fvg in self.bearish_fvgs[:]:
                        if current_datetime >= fvg['Datetime'] and current_datetime.date() == fvg['Datetime'].date():
                            # Ensure relevant data is up to date
                            relevant_data = df.loc[fvg['Datetime']:pd.Timestamp(f"{current_date} {self.start_time}").tz_localize('America/New_York'), 'Close']
                            # print(f'This is relevant data: {relevant_data}')
                            # Check the conditions separately for debugging

                            # if not (relevant_data.loc[fvg['Datetime']] > fvg['First Candle Low']).any():
                            if not (relevant_data > fvg['First Candle Low']).any():
                                
                                # print("Condition 1 passed: No close prices above First Candle Low")
                                # print(f'Current datetime {current_datetime}, fvg first candle low {fvg['First Candle Low']}, Current Close; {current_close}')
                                if current_close > fvg['First Candle Low'] and current_close > current_open:
                                    # print("Condition 2 passed: Current close is above First Candle Low")
                                    self.buy(sl=long_sl_price, tp=long_tp_price)
                                    print(current_time)
                                    print(f"Buy signal placed at {self.data.index[-1]} for Bearish FVG: {fvg}")
                                    self.bearish_fvgs.remove(fvg)
                                    self.last_trade_date = current_date
                                    break
                                else:
                                    pass
                                    # print("Condition 2 failed: Current close is not above First Candle Low")
                            else:
                                pass
                                # print("Condition 1 failed: Some close prices are above First Candle Low")

                    # Check for a valid Bullish FVG trade signal
                    for fvg in self.bullish_fvgs[:]:
                        if current_datetime >= fvg['Datetime'] and current_datetime.date() == fvg['Datetime'].date():
                            # Ensure relevant data is up to date
                            relevant_data = df.loc[fvg['Datetime']:pd.Timestamp(f"{current_date} {self.start_time}").tz_localize('America/New_York'), 'Close']

                            # Check the conditions separately for debugging
                            # Basically if the fvg is not invalidated is this first condition. 

                            #if not (relevant_data.loc[fvg['Datetime']] < fvg['First Candle High']).any(): #.any is like any instance of?
                            if not (relevant_data < fvg['First Candle High']).any():
                                print('Evaluating if relevant data is > fvg first candle low ')
                                # print("Condition 1 passed: No close prices below First Candle High")
                                # Second condition that checks if bullish fvg is closed below triggers sell signal. 
                                if current_close < fvg['First Candle High'] and current_close < current_open:
                                    # print("Condition 2 passed: Current close is below First Candle High")
                                    self.sell(sl=short_sl_price, tp=short_tp_price)
                                    print(f"Sell signal placed at {self.data.index[-1]} for Bullish FVG: {fvg}")
                                    self.bullish_fvgs.remove(fvg)
                                    self.last_trade_date = current_date
                                    break
                                else:
                                    ...
                                    # print("Condition 2 failed: Current close is not below First Candle High")
                            else:
                                ...
                                # print("Condition 1 failed: Some close prices are below First Candle High")


# Params = {} needs to be the format for additional parameters for backtest library
def run_backtest(intraday_data, bullish_fvgs, bearish_fvgs):
    print(f"Type of intraday_data: {type(intraday_data)}")

    print("Preview of intraday_data:")
    print(intraday_data.head())
    
    # Set the class parameters:
    fiveMinFVG.bullish_fvgs = bullish_fvgs
    fiveMinFVG.bearish_fvgs = bearish_fvgs
    # print('This is the bullish fvgs in run backtest funciton')
    # print(fiveMinFVG.bullish_fvgs)

    # print('This is the bearish fvgs in run backtest funciton')
    # print(fiveMinFVG.bearish_fvgs)

    # TODO: Play around with param trade_on close, it's defaulted to false. You could put it to true in the future

    bt = Backtest(intraday_data, fiveMinFVG, cash=100_000) #!! IMPORTANT CASH NEEDS OT BE 100,000 FOR MARGIN, OR YOU CAN SET MARGIN MANUALLY
    stats = bt.run() # Idk if this is right, the datatype might have to be pd series. 


    print(stats)

    # bt.fig_ohlc.xaxis.formatter = DatetimeTickFormatter(days='%d %b')
    # bt.plot()

    # GPT recommended this to fix the error: 
   