import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter
import numpy as np
from graphs import Graphs


# NOTE: MEDIAN DATA WILL ONLY BE DIFFERENT THAN MEAN DATA IF THERE IS MORE THAN 2 VALUES TO EVALUATE, i.e. more than 2 weeks. 

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def display_data_text(ticker_input, time_input, lookback_input, intraday_start_time, intraday_end_time, avg_intraday_range, avg_daily_range, avg_dr_by_day, avg_intraday_range_by_day, intraday_data):
    display_daily_data(ticker_input, time_input, lookback_input, avg_daily_range, avg_dr_by_day)
    if intraday_data is not None:
        display_intraday_data(ticker_input, time_input, lookback_input, intraday_start_time, intraday_end_time, avg_intraday_range, avg_daily_range, avg_dr_by_day, avg_intraday_range_by_day)

def display_median_data_text(ticker_symbol, time, lookback, intraday_start_time, intraday_end_time, median_dr, median_dr_by_day, median_intraday_range, median_intraday_range_by_day, intraday_data):
    display_daily_median_data(ticker_symbol, time, lookback, median_dr, median_dr_by_day)
    if intraday_data is not None:
        display_intraday_median_data(ticker_symbol, time, lookback, intraday_start_time, intraday_end_time, median_dr, median_dr_by_day, median_intraday_range, median_intraday_range_by_day)



def display_charts(avg_dr_by_day, time, lookback, ticker_symbol, avg_daily_range, avg_idr_by_day, intraday_data, intraday_start_time, intraday_end_time, median_dr, median_dr_by_day, median_idr_by_day):

   # TODO: you should be able to make a charts class, because there's a lot of repeated code, and it would make code more readable and show you know OOP.  
    # Instantiate graphs class
    graphs = Graphs(ticker_symbol, time, lookback, intraday_start_time, intraday_end_time)

    # Single data graphs
    graphs.display_avg_dr(avg_dr_by_day)
    graphs.display_median_dr(median_dr_by_day)
    graphs.display_avg_idr(avg_idr_by_day)
    graphs.display_median_idr(median_idr_by_day)

    # Comparison graphs
    graphs.display_avg_dr_and_avg_idr(avg_dr_by_day, avg_idr_by_day)
    graphs.display_median_dr_and_median_idr(median_dr_by_day, median_idr_by_day)
    graphs.display_avg_dr_and_median_dr(avg_dr_by_day, median_dr_by_day)
    graphs.display_avg_idr_and_median_idr(avg_idr_by_day, median_idr_by_day)
    
    #  display_daily_avg_ranges_chart(avg_dr_by_day, time, lookback, ticker_symbol) 
    #  display_daily_median_chart(median_dr_by_day, time, lookback, ticker_symbol) 
    #  display_intraday_avg_ranges_chart(avg_intraday_range_by_day, intraday_start_time, intraday_end_time, ticker_symbol, lookback, time) 
    #  display_intraday_median_chart(intraday_start_time, intraday_end_time, ticker_symbol, time, lookback, median_intraday_range_by_day) 
    # display_avg_dr_and_avg_idr_chart(avg_dr_by_day, avg_intraday_range_by_day) 
    # display_daily_and_intraday_median_chart(intraday_start_time, intraday_end_time, ticker_symbol, time, lookback, median_dr_by_day, median_intraday_range_by_day)
    # display_avg_dr_and_median_dr(avg_dr_by_day, median_dr_by_day, time, lookback, ticker_symbol)
    #display_avg_idr_and_median_idr(avg_intraday_range_by_day, median_intraday_range_by_day, time, lookback, ticker_symbol, intraday_start_time, intraday_end_time)

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
            print(f"The average intraday range from {intraday_start_time}-{intraday_end_time} for {day}s in the past {time}{lookback} is: {avg_intraday_range_by_day[day]:.2f}")

    print(f'\n{intraday_start_time}-{intraday_end_time} makes up {avg_intraday_range / avg_dr  * 100:.2f}% of the daily range on average over the past {time}{lookback}')
    for day in days_of_week:
        if day in avg_dr_by_day.index and day in avg_intraday_range_by_day.index:
            intraday_percentage = avg_intraday_range_by_day[day] / avg_dr_by_day[day] * 100
            print(f"{day.upper()}: {intraday_start_time}-{intraday_end_time} makes up {intraday_percentage:.2f}% of {day}'s range over the past {time}{lookback}")
        else:
            print(f'No data available for {day} in selected lookback period.')


def display_daily_median_data(ticker_symbol, time, lookback, median_dr, median_dr_by_day):
    days_of_week = DAYS_OF_WEEK
    print(f'\nThe median daily range of {ticker_symbol} from the past {lookback}{time} is: {median_dr:.2f}')
    for day in days_of_week:
        # TODO: if user only selefcts a lookback period of a couple days, an error will come, because not all days of week is being selected. need to fix. 
        if day in median_dr_by_day.index:
            print(f'The median daily range for {day} is {median_dr_by_day[day]:.2f}')
        else:
            print(f'No data available for {day} in selected lookback period. ')

def display_intraday_median_data(ticker_symbol, time, lookback, intraday_start_time, intraday_end_time, median_dr, median_dr_by_day, median_intraday_range, median_intraday_range_by_day):
    days_of_week = DAYS_OF_WEEK
    print(f'\nThe median intraday range from {intraday_start_time}-{intraday_end_time} range of {ticker_symbol} from the past {lookback}{time} is: {median_intraday_range:.2f}')
    for day in days_of_week:
        if day in median_intraday_range_by_day.index:
            print(f"The median intraday range from {intraday_start_time}-{intraday_end_time} for {day}s in the past {lookback}{time} is: {median_intraday_range_by_day[day]:.2f}")
