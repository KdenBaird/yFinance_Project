import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter

MIN_FVG_SIZE = 0.10
def adjust_to_previous_trading_day(start_date):
    nyse = mcal.get_calendar('NYSE')
    valid_days = nyse.valid_days(start_date=start_date - pd.DateOffset(days=7), end_date=start_date)
    
    if start_date not in valid_days:
        start_date = valid_days[-1]
    return start_date

def get_daily_data(ticker_symbol, time, lookback):
    end_date = pd.Timestamp.today()
    if time == 'D':
        start_date = end_date - pd.DateOffset(days=lookback)
    elif time == 'M':
        start_date = end_date - pd.DateOffset(months=lookback)
    elif time == 'Y':
        start_date = end_date - pd.DateOffset(years=lookback)

    start_date = adjust_to_previous_trading_day(start_date)
    start_date = start_date.tz_convert('America/New_York')

    if end_date.tzinfo is None:
        end_date = end_date.tz_localize('America/New_York')
    
    daily_data = yf.download(ticker_symbol, start=start_date, end=end_date, progress=False)
    
    if isinstance(daily_data.columns, pd.MultiIndex):
        if daily_data.columns.nlevels >= 2:
            level_0 = daily_data.columns.get_level_values(0)
            level_1 = daily_data.columns.get_level_values(1)
            
            expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if any(col in level_1 for col in expected_cols):
                daily_data.columns = level_1
            elif any(col in level_0 for col in expected_cols):
                daily_data.columns = level_0
            else:
                daily_data.columns = daily_data.columns.get_level_values(-1)
        else:
            daily_data.columns = daily_data.columns.droplevel(0)
    
    if isinstance(daily_data.columns, pd.MultiIndex):
        daily_data.columns = [str(col[-1]) if isinstance(col, tuple) else str(col) for col in daily_data.columns]
    
    if 'Adj Close' in daily_data.columns:
        daily_data = daily_data.drop(columns=['Adj Close'])
    required_cols = ['Open', 'High', 'Low', 'Close']
    missing_cols = [col for col in required_cols if col not in daily_data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns after processing: {missing_cols}. "
                        f"Available columns: {list(daily_data.columns)}. "
                        f"Original column type: {type(daily_data.columns)}")

    if daily_data.index.tzinfo is None:
        daily_data.index = daily_data.index.tz_localize('America/New_York')
    else:
        daily_data.index = daily_data.index.tz_convert('America/New_York') 
    return daily_data, start_date, end_date 

def get_intraday_data(ticker_symbol, start_date, end_date, start_time, end_time):
    end_date = pd.Timestamp.today()
    if start_date.tzinfo is None:
        start_date = start_date.tz_localize('America/New_York')
    else:
        start_date = start_date.tz_convert('America/New_York')

    if end_date.tzinfo is None:
        end_date = end_date.tz_localize('America/New_York')
    else:
        end_date = end_date.tz_convert('America/New_York')
    
    full_day_data = yf.download(ticker_symbol, start=start_date, end=end_date, interval='5m', progress=False)
    
    if isinstance(full_day_data.columns, pd.MultiIndex):
        if full_day_data.columns.nlevels >= 2:
            level_0 = full_day_data.columns.get_level_values(0)
            level_1 = full_day_data.columns.get_level_values(1)
            
            expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if any(col in level_1 for col in expected_cols):
                full_day_data.columns = level_1
            elif any(col in level_0 for col in expected_cols):
                full_day_data.columns = level_0
            else:
                full_day_data.columns = full_day_data.columns.get_level_values(-1)
        else:
            full_day_data.columns = full_day_data.columns.droplevel(0)
    
    if isinstance(full_day_data.columns, pd.MultiIndex):
        full_day_data.columns = [str(col[-1]) if isinstance(col, tuple) else str(col) for col in full_day_data.columns]
    
    if 'Adj Close' in full_day_data.columns:
        full_day_data = full_day_data.drop(columns=['Adj Close'])

    if full_day_data.index.tzinfo is None:
        full_day_data.index = full_day_data.index.tz_localize('America/New_York')
    else:
        full_day_data.index = full_day_data.index.tz_convert('America/New_York')

    full_day_data_for_fvg = full_day_data.copy()
    intraday_data = full_day_data.between_time(start_time, end_time)
    
    if intraday_data.empty:
        print(f'No intraday data available for {ticker_symbol} between {start_time} and {end_time} validate that {ticker_symbol} trades after market hours. ')
        retry = input('Please select "yes" to select a different time range, or "no" to not receive intraday data. ')
        if retry.lower() == 'yes': 
            from user_input import get_intraday_times
            intraday_start_time, intraday_end_time = get_intraday_times()
            return get_intraday_data(ticker_symbol, start_date, end_date, intraday_start_time, intraday_end_time)
        else: 
            print('Exiting intraday data retrieval...')
            return None, None
    
    return intraday_data, full_day_data_for_fvg

def get_extended_intraday_data(ticker, start_date, end_date, interval="1m"):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    all_data = pd.DataFrame()

    while start_date < end_date:
        chunk_end_date = start_date + pd.DateOffset(days=59)
        if chunk_end_date > end_date:
            chunk_end_date = end_date

        data = yf.download(ticker, start=start_date, end=chunk_end_date, interval=interval, progress=False)
        
        if isinstance(data.columns, pd.MultiIndex):
            if data.columns.nlevels >= 2:
                data.columns = data.columns.get_level_values(-1)
            else:
                data.columns = data.columns.droplevel(0)
        
        if 'Adj Close' in data.columns:
            data = data.drop(columns=['Adj Close'])
        
        all_data = pd.concat([all_data, data])
        start_date = chunk_end_date

    return all_data

def find_intraday_hod_lod_times(intraday_data):
    intraday_results = []
    grouped = intraday_data.groupby(intraday_data.index.date)

    for date, group in grouped:
        time_of_high = group['High'].idxmax().time()
        time_of_low = group['Low'].idxmin().time()

        high_at_time_of_high = group.loc[group['High'].idxmax(), 'High']
        low_at_time_of_low = group.loc[group['Low'].idxmin(), 'Low']

        opening_price = group.iloc[0]['Open']
        closing_price = group.iloc[-1]['Close']

        intraday_results.append({
            'Date': date,
            'Time_of_High': time_of_high,
            'High_at_Time_of_High': high_at_time_of_high,
            'Time_of_Low': time_of_low,
            'Low_at_Time_of_Low': low_at_time_of_low,
            'Opening_Price' : opening_price,
            'Closing_Price' : closing_price
        })

    intraday_hod_lod_df = pd.DataFrame(intraday_results)
    return intraday_hod_lod_df

def check_intraday_bullish_fvgs(intraday_data):
    bullish_fvgs = []
    
    if intraday_data.empty:
        return bullish_fvgs
    
    intraday_data_copy = intraday_data.copy()
    intraday_data_copy['Date'] = intraday_data_copy.index.date
    grouped = intraday_data_copy.groupby('Date')
    
    total_candles_checked = 0
    potential_fvgs = 0

    for date, group in grouped:
        group = group.sort_index()
        
        if len(group) < 3:
            continue

        for i in range(len(group) - 2):
            total_candles_checked += 1
            first_candle = group.iloc[i]
            second_candle = group.iloc[i + 1]
            third_candle = group.iloc[i + 2]

            if first_candle['High'] < third_candle['Low']:
                fvg_size = third_candle['Low'] - first_candle['High']
                potential_fvgs += 1
                if fvg_size > MIN_FVG_SIZE:
                    bullish_fvgs.append({ 
                        'Datetime': third_candle.name,
                        'First Candle High': float(first_candle['High']),
                        'Third Candle Low': float(third_candle['Low']),
                        'FVG Range': (float(first_candle['High']), float(third_candle['Low'])),
                        'FVG Size': float(fvg_size)
                    })
    
    return bullish_fvgs

def check_intraday_bearish_fvgs(intraday_data):
    bearish_fvgs = []

    if intraday_data.empty:
        return bearish_fvgs

    intraday_data_copy_bearish = intraday_data.copy()
    intraday_data_copy_bearish['Date'] = intraday_data_copy_bearish.index.date
    grouped = intraday_data_copy_bearish.groupby('Date')
    
    total_candles_checked = 0
    potential_fvgs = 0

    for date, group in grouped:
        group = group.sort_index()
        
        if len(group) < 3:
            continue
        
        for i in range(len(group) - 2):
            total_candles_checked += 1
            first_candle = group.iloc[i]
            second_candle = group.iloc[i + 1]
            third_candle = group.iloc[i + 2]
            
            if first_candle['Low'] > third_candle['High']:
                fvg_size = first_candle['Low'] - third_candle['High']
                potential_fvgs += 1
                if fvg_size > MIN_FVG_SIZE:
                    bearish_fvgs.append({
                        'Datetime': third_candle.name,
                        'First Candle Low': float(first_candle['Low']),
                        'Third Candle High': float(third_candle['High']),
                        'FVG Range': (float(first_candle['Low']), float(third_candle['High'])),
                        'FVG Size': float(fvg_size)
                    })

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