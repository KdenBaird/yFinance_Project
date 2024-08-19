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
import calculations
import display_data


"""
 TODO: Come up with some sort of UI to allow users to specify the data they want to find, examples: certain time of day, certain ticker, 
 how long they want to lookback, certain days of the week, some kind of box that says: "which ticker would you like to use and save as variable to use", or 
 "How far would you like to lookback?"
 - Would like to display in print statements what they specifically selected ie lookaback, ticker, etc.
 - Maybe let users select multiple asset classes to evaluate data, to see how correlating or opposite asset classes data compare. Use threading for this?
"""
# TODO: today's date isn't included in the data. so if lookback period is 5 days it's 5 days from today, yes, but not including today in output or calculations.

# TODO: when you enter an invalid date for intraday data e.g. after hours for microsoft it will prompt the user to create a new one, but then once you do after running calculations there's an error. 

def seasonal_tendencies():
    pass

def main():
    intraday_choice, ticker_input, time_input, lookback_input = user_input.get_user_input()
    data, start_date, end_date = get_data.get_daily_data(ticker_input, time_input, lookback_input)
    # data = calculations.filter_trading_days(data, start_date, end_date)

    # Initialize None variables
    intraday_data = intraday_start_time = intraday_end_time = avg_intraday_range = avg_intraday_range_by_day = None

    if intraday_choice == 'yes':
        intraday_start_time, intraday_end_time = user_input.get_intraday_times()
        intraday_data = get_data.get_intraday_data(ticker_input, start_date, end_date, intraday_start_time, intraday_end_time)
        # TODO: perhaps change the return variable of this to "filtered_data" to keep the raw data 
        if intraday_data is None: # get_data.get_intraday_data() offers the user the opportunity to make intraday_data to None
            intraday_data = calculations.filter_trading_days(intraday_data, start_date, end_date)
            intraday_data = intraday_start_time = intraday_end_time = avg_intraday_range = avg_intraday_range_by_day = None

        # Calculations for intraday data
        avg_intraday_range = calculations.intraday_calculations(intraday_data)
        avg_intraday_range_by_day = calculations.calculate_avg_intraday_range_by_day(intraday_data)

    avg_daily_range = calculations.calculate_avg_dr(data)
    avg_dr_by_day = calculations.calculate_avg_dr_by_day(data)

    display_data.display_data_text(ticker_input, time_input, lookback_input, intraday_start_time, intraday_end_time, avg_intraday_range, avg_daily_range, avg_dr_by_day, avg_intraday_range_by_day, intraday_data)
    display_data.display_charts()
    
if  __name__ == '__main__':
    main()
    