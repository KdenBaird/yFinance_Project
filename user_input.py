import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter

def  get_user_input():
    while True:
        ticker_input = input('What ticker symbol would you like to grab data from? (e.g. if I would like Microsoft I would enter "MSFT") ').upper()
        try:
            ticker = yf.Ticker(ticker_input)
            data = ticker.history(period = '1d')
            if data.empty:
                print(f'{ticker_input} is an invalid ticker symbol')
            else:
                break
        except Exception as e:
            
            print(f'An error occured: {e}. Please try again.')
    while True:
        time_input = input('Would you like to look back in days, months, or years to calculate the average daily candle range? Type "D", "M" or "Y" ')
        if time_input.upper() in ['D', 'M', 'Y']:
            break
        else:
            print('Invalid time, please try again.')
    while True:
        lookback_input = input('How far would you like to lookback to get data from? (e.g., enter "10" for 10 days, "3" for 3 months, etc.) ')
        try:
            lookback_input = int(lookback_input)
            break
        except ValueError:
            print('Lookback value must be an integer. Please try again.')
    while True:
    #     # TODO: rename this maybe?
        intraday_choice = input('Would you like to receive intraday data for a chosen time period? (Max lookback for data is 59 days if you choose this.) Type "yes" or "no" ').strip().lower()
        if intraday_choice not in ['yes', 'no']:
            print(f'{intraday_choice} must be "yes" or "no"')
        else:
            return intraday_choice, ticker_input, time_input.upper(), lookback_input
    # # TODO: if intraday_choice = yes return intradaystart and end time, if false, don't return it and don't run intraday data analysis

def get_intraday_times():
    while True:
        intraday_start_time = input(
        'What would you like the start time to be? (Must at least be in increments of 5 minutes and is calculated in Eastern Time) e.g. "09:30"'
        ' Note: time is on a 24 hour clock to get data from 2 AM you must type "02:00" or to get data from 4:00 PM  you must type "14:00": '
        )
        if validate_time_format(intraday_start_time):
            break
        else:
            print('Please enter a valid time format. Time should be in "HH:MM" format.')
    while True:
        intraday_end_time = input(
        'What would you like the end time to be? (Must at least be in increments of 5 minutes and is calculated in Eastern Time) e.g. "09:30" '
        ' Note: time is on a 24 hour clock to get data from 2 AM you must type "02:00" or to get data from 4:00 PM  you must type "14:00": '
        )
        if validate_time_format(intraday_end_time):
            break
        else: 
            print('Please enter a valid time format. Time should be in "HH:MM" format.')
    return intraday_start_time, intraday_end_time
    
def validate_time_format(time_str):
    try:
        # Validate that the input is in 'HH:MM' format
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False
