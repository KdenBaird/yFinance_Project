import pandas as pd
import pandas_market_calendars as mcal

def filter_trading_days(data, start_date, end_date):
    data = data[data.index.weekday < 5]
    nyse = mcal.get_calendar('NYSE')
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    valid_trading_days = nyse.valid_days(start_date=start_date_str, end_date=end_date_str, tz='America/New_York')

    if isinstance(valid_trading_days, pd.Timestamp):
        valid_trading_days = [valid_trading_days]

    valid_trading_days_index = pd.DatetimeIndex(valid_trading_days)

    if data.index.freq is None:
        data = data[data.index.normalize().isin(valid_trading_days_index)]
    else:
        data_dates = data.index.normalize()
        data = data[data_dates.isin(valid_trading_days_index)]

    return data

def calculate_avg_dr(data):
    data = data[data.index.date < pd.Timestamp.today().date()].copy()
    daily_ranges = pd.Series([high - low for high, low in zip(data['High'], data['Low'])])
    avg_dr = round(daily_ranges.mean(), 2)
    return avg_dr, daily_ranges

def calculate_avg_dr_by_day(data):
    data.loc[:, 'Daily_Range'] = data['High'] - data['Low']
    data.loc[:, 'Day_of_Week'] = data.index.day_name()

    dr_by_day = data.groupby('Day_of_Week')['Daily_Range']
    avg_dr_by_day = round(dr_by_day.mean(), 2)
    return avg_dr_by_day, dr_by_day

def calculate_avg_intraday_range(intraday_data):
    intraday_data = intraday_data[intraday_data.index.date < pd.Timestamp.today().date()].copy()
    intraday_ranges = intraday_data.groupby(intraday_data.index.date).apply(
        lambda x: round(x['High'].max() - x['Low'].min(), 2)
    )
    avg_intraday_range = intraday_ranges.mean()
    return intraday_data, avg_intraday_range, intraday_ranges

def calculate_avg_intraday_range_by_day(intraday_data, data):
    intraday_ranges_df = data.copy()
    intraday_ranges_df['Day_of_Week'] = intraday_ranges_df.index.day_name()

    intraday_ranges = intraday_data.groupby(intraday_data.index.date).apply(
        lambda x: round(x['High'].max() - x['Low'].min(), 2)
    )
   
    intraday_ranges_df['Intraday_Range'] = intraday_ranges.reindex(intraday_ranges_df.index.date).values
    intraday_range_by_day = intraday_ranges_df.groupby('Day_of_Week')['Intraday_Range']
    avg_intraday_range_by_day = intraday_range_by_day.mean()
    return avg_intraday_range_by_day, intraday_range_by_day

def calculate_median_dr(daily_ranges):
    median_dr = round(daily_ranges.median(), 2)
    return median_dr

def calculate_median_dr_by_day(dr_by_day):
    median_dr_by_day = round(dr_by_day.median(), 2)
    return median_dr_by_day

def calculate_median_intraday_range(intraday_ranges):
    median_intraday_range = round(intraday_ranges.median(), 2)
    return median_intraday_range

def calculate_median_intraday_range_by_day(intraday_range_by_day):
    median_intraday_range_by_day = round(intraday_range_by_day.median(), 2)
    return median_intraday_range_by_day

def calculate_median_bearish_reversal_time(data):
    data['Time_of_High'] = pd.to_datetime(data['Time_of_High'], format='%H:%M:%S').dt.time
    data['Time_of_Low'] = pd.to_datetime(data['Time_of_Low'], format='%H:%M:%S').dt.time

    bearish_days = data[data['Opening_Price'] > data['Closing_Price']]

    if not bearish_days.empty:
        time_in_seconds = bearish_days['Time_of_High'].apply(lambda t: t.hour * 3600 + t.minute * 60 + t.second)
        median_seconds = time_in_seconds.median()
        median_time_of_high = pd.to_datetime(median_seconds, unit='s').time()
        return median_time_of_high
    else:
        return None

def calculate_median_bullish_reversal_time(data):
    data['Time_of_High'] = pd.to_datetime(data['Time_of_High'], format='%H:%M:%S').dt.time
    data['Time_of_Low'] = pd.to_datetime(data['Time_of_Low'], format='%H:%M:%S').dt.time

    bullish_days = data[data['Closing_Price'] > data['Opening_Price']]

    if not bullish_days.empty:
        time_in_seconds = bullish_days['Time_of_Low'].apply(lambda t: t.hour * 3600 + t.minute * 60 + t.second)
        median_seconds = time_in_seconds.median()
        median_time_of_low = pd.to_datetime(median_seconds, unit='s').time()
        return median_time_of_low
    else:
        return None