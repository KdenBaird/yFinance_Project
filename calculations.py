import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter


def filter_trading_days(data, start_date, end_date):
    pass
    # CHAT GPT did this function for me (I got impatient)
    start_date = start_date.tz_localize('America/New_York') if start_date.tzinfo is None else start_date
    end_date = end_date.tz_localize('America/New_York') if end_date.tzinfo is None else end_date
    
    # Filter out weekends (Saturday = 5, Sunday = 6)
    data = data[data.index.weekday < 5]

    # Fetch the NYSE calendar (you can adjust this based on your market)
    nyse = mcal.get_calendar('NYSE')

    # if data.index.tzinfo is None:
    #     start_date = pd.Timestamp(start_date).tz_localize('America/New_York')
    #     end_date = pd.Timestamp(end_date).tz_localize('America/New_York')
    # else:
    #     start_date = pd.Timestamp(start_date).tz_convert('America/New_York')
    #     end_date = pd.Timestamp(end_date).tz_convert('America/New_York')
    # Define the date range for holidays

    # Get valid trading days (excluding weekends and holidays)
    """
    # WHEN I USED TZ AS AN ARGUMENT AND SET IT TO AMERICA/NY i got typeerror: "Already tz-aware use tz_convert to convert" I only got this error AFTER i chose intraday times, which means this code properly ran on daily data, 
    # Which means for some reason it's not converting on daily data. 
    """
    valid_trading_days = nyse.valid_days(start_date=start_date, end_date=end_date)

    if data.index.freq is None:  # Likely daily data
        data = data[data.index.normalize().isin(valid_trading_days)]
    else:  # Likely intraday data
        # Convert to just dates (dropping time part) for filtering
        data_dates = data.index.normalize()
        data = data[data_dates.isin(valid_trading_days)]

    return data

def calculate_avg_dr(data):
    # Need to exclude today's data from both datasets to ensure intraday data and data use same dates
    data = data[data.index.date < pd.Timestamp.today().date()]

    # STUDY THIS LINE, LIST COMPREHENSION, THIS VS 4 LINES OF CODE
    daily_ranges = pd.Series([high - low for high, low in zip(data['High'], data['Low'])])

    print('This is the "daily ranges" this is in CALCULATE_AVG_DR function which is basically a for loop and subtracts the high and low of df: ')
    print(daily_ranges)

    avg_dr = daily_ranges.mean()
    print('This is the avg_dr head which takes the "daily_ranges.mean(): ')
    print(avg_dr)
    return avg_dr

def calculate_avg_dr_by_day(data):
    print(f'Df "data" before creating new Daily Range Column and Day of Week column')
    print(data)

    data['Daily_Range'] = data['High'] - data['Low']
    data['Day_of_Week'] = data.index.day_name()
    print(f'Df "data" after  creating new Daily Range Column and Day of Week column')
    print(data)

    avg_dr_by_day = data.groupby('Day_of_Week')['Daily_Range'].mean()
    print('This CALCULATE_AVG_DR_BY_DAY function is grouping Daily_Range column, and Daily_Week column Here is avg_dr_by_day:')
    print('Note: I am applying .mean() function to this I might not be applying this properly so if data is weird, this is why')
    print(avg_dr_by_day)
    return avg_dr_by_day

def intraday_calculations(intraday_data):
     # Need to exclude today's data from both datasets to ensure intraday data and data use same dates
    intraday_data = intraday_data[intraday_data.index.date < pd.Timestamp.today().date()]

    # Group by the date and calculate the AM range become more comfy w lambda
    intraday_ranges = intraday_data.groupby(intraday_data.index.date).apply(
    lambda x: round(x['High'].max() - x['Low'].min(), 2)
    )
    avg_intraday_range = intraday_ranges.mean()
    return avg_intraday_range

def calculate_avg_intraday_range_by_day(intraday_data):
    print('This is intraday_data before adding intraday range, and day of week column')
    print(intraday_data)

    intraday_data['Intraday_Range'] = intraday_data['High'] - intraday_data['Low']
    intraday_data['Day_of_Week'] = intraday_data.index.day_name()

    print('This is intraday_data after adding intraday range, and day of week column')
    print(intraday_data)

    print('This is CALCULATE AVG_INTRADAY_RANGE_BY_DAY function here is avg intraday range variable after grouping day of week and intraday range.')
    print('Note: I am applying .mean() function to this I might not be applying this properly ')
    avg_intraday_range_by_day = intraday_data.groupby('Day_of_Week')['Intraday_Range'].mean()
    print(avg_intraday_range_by_day)

    return avg_intraday_range_by_day