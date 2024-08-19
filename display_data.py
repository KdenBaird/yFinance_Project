import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def display_data_text(ticker_input, time_input, lookback_input, intraday_start_time, intraday_end_time, avg_intraday_range, avg_daily_range, avg_dr_by_day, avg_intraday_range_by_day, intraday_data):
    display_daily_data(ticker_input, time_input, lookback_input, avg_daily_range, avg_dr_by_day)
    if intraday_data is not None:
        display_intraday_data(ticker_input, time_input, lookback_input, intraday_start_time, intraday_end_time, avg_intraday_range, avg_daily_range, avg_dr_by_day, avg_intraday_range_by_day)

def display_charts():
    display_daily_chart()
    display_intraday_chart()

def display_daily_data(ticker_symbol, lookback, time, avg_dr, avg_dr_by_day):
    days_of_week = DAYS_OF_WEEK
    print(f'\nThe average daily range of {ticker_symbol} from the past {time}{lookback} is: {avg_dr:.2f}')
    for day in days_of_week:
        # TODO: if user only selefcts a lookback period of a couple days, an error will come, because not all days of week is being selected. need to fix. 
        if day in avg_dr_by_day.index:
            print(f'The average daily range for {day} is {avg_dr_by_day[day]:.2f}')
        else:
            print(f'No data available for {day} in selected lookback period. ')

def display_intraday_data(ticker_symbol, lookback, time, intraday_start_time, intraday_end_time, avg_intraday_range, avg_dr, avg_dr_by_day, avg_intraday_range_by_day):
    days_of_week = DAYS_OF_WEEK
    print(f'\nThe average intraday range from {intraday_start_time}-{intraday_end_time} range of {ticker_symbol} from the past {time}{lookback} is: {avg_intraday_range:.2f}')
    for day in days_of_week:
        if day in avg_intraday_range_by_day.index:
            print(f'The average intraday range from {intraday_start_time}-{intraday_end_time} for {day} is {avg_intraday_range_by_day[day]:.2f}')

    print(f'\n{intraday_start_time}-{intraday_end_time} makes up {avg_intraday_range / avg_dr  * 100:.2f}% of the daily range on average over the past {time}{lookback}')
    for day in days_of_week:
        if day in avg_dr_by_day.index and day in avg_intraday_range_by_day.index:
            intraday_percentage = avg_intraday_range_by_day[day] / avg_dr_by_day[day] * 100
            print(f"{day.upper()}: {intraday_start_time}-{intraday_end_time} makes up {intraday_percentage:.2f}% of {day}'s range over the past {time}{lookback}")
        else:
            print(f'No data available for {day} in selected lookback period.')

# TODO: display charts
def display_daily_chart():
    pass
    days_axis = DAYS_OF_WEEK
    dr_axis = None

def display_intraday_chart():
    days_axis = DAYS_OF_WEEK