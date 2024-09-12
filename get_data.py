import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter

MIN_FVG_SIZE = 5
def adjust_to_previous_trading_day(start_date):
    # Fetch the NYSE calendar
    nyse = mcal.get_calendar('NYSE')
    
    # Get valid trading days around the `start_date`
    valid_days = nyse.valid_days(start_date=start_date - pd.DateOffset(days=7), end_date=start_date)
    
    # If `start_date` is not a valid trading day, find the closest previous trading day
    if start_date not in valid_days:
        start_date = valid_days[-1]  # Last valid trading day before the current `start_date`
    return start_date

# TODO: timezone conversion is affecting data, for some reason taking out fridays, but i need time zone conversion to subtract holidays and potentially fix another bug to align intraday data time and dr data time
def get_daily_data(ticker_symbol, time, lookback):
    end_date = pd.Timestamp.today()
    if time == 'D':
        start_date = end_date - pd.DateOffset(days=lookback)
    elif time == 'M':
        start_date = end_date - pd.DateOffset(months=lookback)
    elif time == 'Y':
        start_date = end_date - pd.DateOffset(years=lookback)

    # Adjust start_date to the previous trading day if it falls on a weekend or holiday
    start_date = adjust_to_previous_trading_day(start_date)
     
    start_date = start_date.tz_convert('America/New_York')

    if end_date.tzinfo is None:
        end_date = end_date.tz_localize('America/New_York')
    #Download the historical data for the given date range
    daily_data = yf.download(ticker_symbol, start=start_date, end=end_date)
    daily_data = daily_data.drop(columns=['Adj Close'])

    if daily_data.index.tzinfo is None:
        daily_data.index = daily_data.index.tz_localize('America/New_York')
    else:
        daily_data.index = daily_data.index.tz_convert('America/New_York') 
    return daily_data, start_date, end_date 


# TODO: getting an assertion error saying times don't match up when i run this. YOOO CHECK IF BOTH THE INTRADAY TIMEZONES AND DAILY RANGE TIME ZONES ARE THE SAME, THIS COULD CAUSE DISCREPANCY W DATA???

def get_intraday_data(ticker_symbol, start_date, end_date, start_time, end_time):
    end_date = pd.Timestamp.today()

     # Ensure start_date and end_date are timezone-aware
    if start_date.tzinfo is None:
        start_date = start_date.tz_localize('America/New_York')
    else:
        start_date = start_date.tz_convert('America/New_York')

    if end_date.tzinfo is None:
        end_date = end_date.tz_localize('America/New_York')
    else:
        end_date = end_date.tz_convert('America/New_York')
    
    intraday_data = yf.download(ticker_symbol, start=start_date, end=end_date, interval='5m')
    intraday_data = intraday_data.drop(columns=['Adj Close'])
    print(f'THIS IS INTRADAY DATA: {intraday_data}')
    # intraday_1m_data = intraday_1m_data = yf.download(ticker_symbol, start=start_date, end=end_date, interval='1m')
    # intraday_data = intraday_1m_data.drop(columns=['Adj Close'])

    # Ensure the DatetimeIndex is timezone-aware (localize if needed)
    if intraday_data.index.tzinfo is None:
        intraday_data.index = intraday_data.index.tz_localize('America/New_York')
        # intraday_1m_data.index = intraday_data.index.tz_localize('America/New_York')
    else:
        intraday_data.index = intraday_data.index.tz_convert('America/New_York')
        # intraday_1m_data.index = intraday_data.index.tz_convert('America/New_York')

    # Filter the data between the specified times
    intraday_data = intraday_data.between_time(start_time, end_time)
    print(f'THIS IS INTRADAY DATA AFTER FILTERING TIME: {intraday_data}')
    
    # If no data is available for selected time range, i.e. they choose a stock, and choose hours outside of market time (9:30 - 4:00)
    if intraday_data.empty:
        print(f'No intraday data available for {ticker_symbol} between {start_time} and {end_time} validate that {ticker_symbol} trades after market hours. ')
        retry = input('Please select "yes" to select a different time range, or "no" to not receive intraday data. ')
        if retry.lower() == 'yes': 
            intraday_start_time, intraday_end_time = get_intraday_times()
            get_intraday_data(ticker_symbol, start_date, end_date, intraday_start_time, intraday_end_time)
        else: 
            print('Exiting intraday data retrieval...')
            intraday_data = None
    return intraday_data

# TODO: There is a way to get more intraday data than 59 days, by concatenating the data from 59 day periods it'll look smth like this:

def get_extended_intraday_data(ticker, start_date, end_date, interval="1m"):
    # Convert dates to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    all_data = pd.DataFrame()

    while start_date < end_date:
        # Define the chunk end date, no more than 59 days from the start
        chunk_end_date = start_date + pd.DateOffset(days=59)
        if chunk_end_date > end_date:
            chunk_end_date = end_date

        # Fetch the data for this chunk
        data = yf.download(ticker, start=start_date, end=chunk_end_date, interval=interval)
        
        # Append to the overall DataFrame
        all_data = pd.concat([all_data, data])

        # Update the start_date for the next loop iteration
        start_date = chunk_end_date

    return all_data
# TODO: only 7 days of 1m data are allowed... 
def find_intraday_hod_lod_times(intraday_data):
    # CHAT GPT made this function for me 
      # Create an empty list to store results
    intraday_results = []

    # Group data by day
    grouped = intraday_data.groupby(intraday_data.index.date)

    for date, group in grouped:
        # Find the time of the highest and lowest price of the day
        time_of_high = group['High'].idxmax().time()
        time_of_low = group['Low'].idxmin().time()

        high_at_time_of_high = group.loc[group['High'].idxmax(), 'High']
        low_at_time_of_low = group.loc[group['Low'].idxmin(), 'Low']

        opening_price = group.iloc[0]['Open']
        closing_price = group.iloc[-1]['Close']

        # Append the results
        intraday_results.append({
            'Date': date,
            'Time_of_High': time_of_high,
            'High_at_Time_of_High': high_at_time_of_high,
            'Time_of_Low': time_of_low,
            'Low_at_Time_of_Low': low_at_time_of_low,
            'Opening_Price' : opening_price,
            'Closing_Price' : closing_price
        })

    # Convert the results to a DataFrame
    intraday_hod_lod_df = pd.DataFrame(intraday_results)
    print('This is what intraday_hod_lod_df looks like: ')
    print(intraday_hod_lod_df)

    print('This is what INTRADAYDATA looks like after find_intraday_hod_lod is being called.')
    print(intraday_data.iloc)

    return intraday_hod_lod_df
"""
Find out how many candles are in each day for intraday data
    PROBLEM IS THE FIRST CANDLE IS STARTING @ 10:55 second cnadle is the 10:00 am candle of the next day, thats why the fvg range. 
     Iterate over the data using a sliding window of 3 consecutive rows
     Maybe create a dict to store the days maybe the datetime index, and for each value within that day run the for i in range. 
     you can possibly use a break in the nested for loop which is inside fo days in dict. You can do if third_candle[columns = time 10:55]
     If I wanted to find the number of candles within the designated time frame I could do the end_time - start_time /5 5 is the num of candlestick intervals. set that equal to numofCandles var
"""
def check_intraday_bullish_fvgs(intraday_data):
    bullish_fvgs = []
    
    # Create a copy of the intraday_data DataFrame
    intraday_data_copy = intraday_data.copy()
    
    # Convert the Datetime index to a date format for grouping
    intraday_data_copy['Date'] = intraday_data_copy.index.date

    # Group the data by date
    grouped = intraday_data_copy.groupby('Date')

    # Iterate over each group (i.e., each day)
    for date, group in grouped:
        # Ensure the group is sorted by time within the day
        group = group.sort_index()

        for i in range(len(group) - 2):
            first_candle = group.iloc[i]
            second_candle = group.iloc[i + 1]
            third_candle = group.iloc[i + 2]

            # Check for Bullish FVG conditions
            if first_candle['High'] < third_candle['Low']:
                fvg_size = third_candle['Low'] - first_candle['High']
                if fvg_size > MIN_FVG_SIZE:
                    bullish_fvgs.append({ 
                        'Datetime': third_candle.name,  # Time of the third candle
                        'First Candle High': float(first_candle['High']),
                        'Third Candle Low': float(third_candle['Low']),
                        'FVG Range': (float(first_candle['High']), float(third_candle['Low'])),
                        'FVG Size': float(fvg_size)
                    })

    print('THIS IS THE BULLISH FVG LIST OF DICTS: ')
    for i in bullish_fvgs:
        print(i)
    
    return bullish_fvgs

def check_intraday_bearish_fvgs(intraday_data):
    bearish_fvgs = []

    intraday_data_copy_bearish = intraday_data.copy()
    
    # Convert the Datetime index to a date format for grouping
    intraday_data_copy_bearish['Date'] = intraday_data_copy_bearish.index.date

    # Group the data by date
    grouped = intraday_data_copy_bearish.groupby('Date')

    # Iterate over each group (i.e., each day)
    for date, group in grouped:
        # Ensure the group is sorted by time within the day
        group = group.sort_index()
        
    # Iterate over the data using a sliding window of 3 consecutive rows
        for i in range(len(group) - 2):
            first_candle = group.iloc[i]
            second_candle = group.iloc[i + 1]
            third_candle = group.iloc[i + 2]
            
            # Check for Bearish FVG conditions
            if first_candle['Low'] > third_candle['High']:
                fvg_size = first_candle['Low'] - third_candle['High']
                # Ensure there's a gap between the first candle's low and the third candle's high
                if fvg_size > 5:
                    bearish_fvgs.append({
                        'Datetime': third_candle.name,  # Time of the third candle
                        'First Candle Low': float(first_candle['Low']),
                        'Third Candle High': float(third_candle['High']),
                        'FVG Range': (float(first_candle['Low']), float(third_candle['High'])),
                        'FVG Size': float(fvg_size)
                    })
    print('THIS IS THE LIST OF BEARISHFVGS')
    
    for i in bearish_fvgs:
        print(i)

    return bearish_fvgs

# TODO: I cannot find the exact time of day when HOD and LOD is created, cus i need intraday data... maybe come back to this idk. 
""""
def find_daily_hod_lod_times(daily_data):
    daily_results = []

    print(f'Here is daily data in daily_HOD_LOD function: {daily_data}')
    grouped = daily_data.groupby(daily_data.index.date)
    print('This is what grouped looks like for daily funciton')
    print(grouped)

    for date, group in grouped:
        time_of_high = group['High'].idxmax().time() # returns the index (which is a Datetime object) where the 'High' column reaches its maximum value for that day. .time extracts the time of datetime object
        time_of_low = group['Low'].idxmin().time()

        high_at_time_of_high = group.loc[time_of_high, 'High']
        low_at_time_of_low = group.loc[time_of_low, 'Low']

        # Append the results (adding dictionaries which basically become rows when converting results to pandas df)
        daily_results.append({
            'Date': date,
            'Time_of_High': time_of_high,
            'High_at_Time_of_High': high_at_time_of_high,
            'Time_of_Low': time_of_low,
            'Low_at_Time_of_Low': low_at_time_of_low 
        })

    # Convert the results to a DataFrame
    data_hod_lod_df = pd.DataFrame(daily_results)
    print('This is what data_hod_lod_df looks like: ')
    print(data_hod_lod_df)
    
    return data_hod_lod_df
"""