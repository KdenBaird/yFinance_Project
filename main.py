import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter

# Other python files
import user_input
import get_data
import calculations as calc
import display_data


"""
 TODO: Come up with some sort of UI to allow users to specify the data they want to find, examples: certain time of day, certain ticker, 
 how long they want to lookback, certain days of the week, some kind of box that says: "which ticker would you like to use and save as variable to use", or 
 "How far would you like to lookback?"
 - Would like to display in print statements what they specifically selected ie lookaback, ticker, etc.
 - Maybe let users select multiple asset classes to evaluate data, to see how correlating or opposite asset classes data compare. Use threading for this?
"""

# TODO: when you enter an invalid date for intraday data e.g. after hours for microsoft it will prompt the user to create a new one, but then once you do after running calculations there's an error. 
def seasonal_tendencies():
    pass

def main():
    intraday_choice, ticker_input, time_input, lookback_input = user_input.get_user_input()
    daily_data, start_date, end_date = get_data.get_daily_data(ticker_input, time_input, lookback_input)
    daily_data = calc.filter_trading_days(daily_data, start_date, end_date)

    # Initialize None variables
    intraday_data = intraday_start_time = intraday_end_time = avg_intraday_range = avg_intraday_range_by_day = None

    if intraday_choice == 'yes':
        intraday_start_time, intraday_end_time = user_input.get_intraday_times()
        intraday_data = get_data.get_intraday_data(ticker_input, start_date, end_date, intraday_start_time, intraday_end_time)
        intraday_hod_lod_df = get_data.find_intraday_hod_lod_times(intraday_data)
        # TODO: perhaps change the return variable of this to "filtered_data" to keep the raw data 
        if intraday_data is None: # get_data.get_intraday_data() offers the user the opportunity to make intraday_data to None
            intraday_data = intraday_start_time = intraday_end_time = avg_intraday_range = avg_intraday_range_by_day = None
        else:
            intraday_data = calc.filter_trading_days(intraday_data, start_date, end_date)
            intraday_data, avg_intraday_range, intraday_ranges = calc.calculate_avg_intraday_range(intraday_data)   
            avg_intraday_range_by_day, intraday_range_by_day = calc.calculate_avg_intraday_range_by_day(intraday_data, daily_data)
            median_intraday_range = calc.calculate_median_intraday_range(intraday_ranges)
            median_intraday_range_by_day = calc.calculate_median_intraday_range_by_day(intraday_range_by_day)

    avg_daily_range, daily_ranges = calc.calculate_avg_dr(daily_data)
    avg_dr_by_day, dr_by_day = calc.calculate_avg_dr_by_day(daily_data)
    median_dr = calc.calculate_median_dr(daily_ranges)
    median_dr_by_day = calc.calculate_median_dr_by_day(dr_by_day)

    display_data.display_data_text(ticker_input, time_input, lookback_input, intraday_start_time, intraday_end_time, avg_intraday_range, avg_daily_range, avg_dr_by_day, avg_intraday_range_by_day, intraday_data)
    display_data.display_median_data_text(ticker_input, time_input, lookback_input, intraday_start_time, intraday_end_time, median_dr, median_dr_by_day, median_intraday_range, median_intraday_range_by_day, intraday_data)
    display_data.display_charts(avg_dr_by_day, time_input, lookback_input, ticker_input, avg_daily_range, avg_intraday_range_by_day, intraday_data, intraday_start_time, intraday_end_time, median_dr, median_dr_by_day, median_intraday_range_by_day)
    
if  __name__ == '__main__':
    main()
    # TODO: date index is 7/1/24, however start index is 6/30 this could be because of my code where the end date is yesterday isntead of today which could lead to my tz error.
    # TODO: I want to add volume calculations... I need to create different df names, because I keep overwriting "data" and "intraday_data" if i can narrow down df I won't need to print the df to see what it contains at what part of my program. 
    # ^^ This will help readability as well and scalability. Create this into classes, and use OOP principles? 
    