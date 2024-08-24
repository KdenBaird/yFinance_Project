import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter

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

    # Ensure the DatetimeIndex is timezone-aware (localize if needed)
    if intraday_data.index.tzinfo is None:
        intraday_data.index = intraday_data.index.tz_localize('America/New_York')
    else:
        intraday_data.index = intraday_data.index.tz_convert('America/New_York')

    # Filter the data between the specified times
    intraday_data = intraday_data.between_time(start_time, end_time)
   
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

def find_intraday_hod_lod_times(intraday_data):
    # CHAT GPT made this function for me 
    # Create an empty list to store results
    results = []

    # Group data by day
    # CB make sure you understand this: the groupby() function in pandas creates a DataFrameGroupBy object, which is essentially a collection of groups where each group is associated with a particular key (in this case, a date). 
    grouped = intraday_data.groupby(intraday_data.index.date)
    print('This is what grouped looks like: ')
    print(grouped)

    # Think of the next block of code as this, for key, value in dict Of the date, we're finding the time in which the value or group's column made the high, and low, and the actual high and low price
    for date, group in grouped:
        # Find the time of the highest and lowest price of the day
        time_of_high = group['High'].idxmax().time() # returns the index (which is a Datetime object) where the 'High' column reaches its maximum value for that day. .time extracts the time of datetime object
        time_of_low = group['Low'].idxmin().time()

        high_at_time_of_high = group.loc[time_of_high, 'High']
        low_at_time_of_low = group.loc[time_of_low, 'Low']

        # Append the results (adding dictionaries which basically become rows when converting results to pandas df)
        results.append({
            'Date': date,
            'Time_of_High': time_of_high,
            'High_at_Time_of_High': high_at_time_of_high,
            'Time_of_Low': time_of_low,
            'Low_at_Time_of_Low': low_at_time_of_low 

        })

    # Convert the results to a DataFrame
    intraday_hod_lod_df = pd.DataFrame(results)
    print('This si what intraday_hod_lod_df looks like: ')
    print(intraday_hod_lod_df)

    return intraday_hod_lod_df