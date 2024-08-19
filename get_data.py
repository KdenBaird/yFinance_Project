import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter


# TODO: timezone conversion is affecting data, for some reason taking out fridays, but i need time zone conversion to subtract holidays and potentially fix another bug to align intraday data time and dr data time
def get_daily_data(ticker_symbol, time, lookback):
    end_date = pd.Timestamp.today()
    if time == 'D':
        start_date = end_date - pd.DateOffset(days=lookback)
    elif time == 'M':
        start_date = end_date - pd.DateOffset(months=lookback)
    elif time == 'Y':
        start_date = end_date - pd.DateOffset(years=lookback)

    # Ensure start_date and end_date are timezone-aware
    # start_date = start_date.tz_localize('America/New_York') if start_date.tzinfo is None else start_date
    # end_date = end_date.tz_localize('America/New_York') if end_date.tzinfo is None else end_date

    #Download the historical data for the given date range
    data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # # Debugging
    # print(data.tail())
    # print("Data for Fridays:")
    # print(data[data.index.day_name() == 'Friday'])
    # print("Original date range:", data.index.min(), "to", data.index.max())

   # Basically, I use localize if tz is naive (not set yet) if it's aware (or localized) just convert to US/NY time
   # TODO: This code is only changing the INDEX need to change start and end_date too
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC').tz_convert('America/New_York')
    else:
        data.index = data.index.tz_convert('America/New_York')
    
    # Debugging
    
    # print("Date range after conversion:", data.index.min(), "to", data.index.max())

    # print(data.tail())
    # print("Data for Fridays:")
    # print(data[data.index.day_name() == 'Friday'])

    # print("Data within trading hours:")
    # print(data.between_time('09:30', '16:00'))


    return data, start_date, end_date

# Filters out weekends and holidays
# TODO: getting an assertion error saying times don't match up when i run this. YOOO CHECK IF BOTH THE INTRADAY TIMEZONES AND DAILY RANGE TIME ZONES ARE THE SAME, THIS COULD CAUSE DISCREPANCY W DATA???

def get_intraday_data(ticker_symbol, start_date, end_date, start_time, end_time):
    intraday_data = yf.download(ticker_symbol, start=start_date, end=end_date, interval='5m')

    # Ensure the DatetimeIndex is timezone-aware (localize if needed)
    # When i use this way to localize, all data is not available. 
    if intraday_data.index.tzinfo is None:
        intraday_data.index = intraday_data.index.tz_localize('UTC').tz_convert('America/New_York')
    else:
        intraday_data.index = intraday_data.index.tz_convert('America/New_York')

    # Convert to Eastern Time (ET)
    #intraday_data = intraday_data.tz_convert('America/New_York')
    # TODO: there are bugs when i enter MSFT as stock, and have certain times. e.g. 12:00 - 02:00 also is there a way to differentiate AM and PM? This might not be fixed yet.
    intraday_data = intraday_data.between_time(start_time, end_time)

    # If no data is available for selected time range, i.e. they choose a stock, and choose hours outside of market time (9:30 - 4:00)
    if intraday_data.empty:
        print(f'No intraday data available for {ticker_symbol} between {start_time} and {end_time} validate that {ticker_symbol} trades after market hours. ')
        retry = input('Please select "yes" to select a different time range, or "no" to not receive intraday data. ')
        if retry == 'yes': 
            intraday_start_time, intraday_end_time = get_intraday_times()
            get_intraday_data(ticker_symbol, start_date, end_date, intraday_start_time, intraday_end_time)
        else: 
            print('Exiting intraday data retrieval...')
            intraday_data = None

    return intraday_data