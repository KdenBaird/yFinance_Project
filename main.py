import user_input
import get_data
import calculations as calc
import display_data
import backtest as bt

def seasonal_tendencies():
    pass

def main():
    intraday_choice, ticker_input, time_input, lookback_input = user_input.get_user_input()
    daily_data, start_date, end_date = get_data.get_daily_data(ticker_input, time_input, lookback_input)
    daily_data = calc.filter_trading_days(daily_data, start_date, end_date)
    
    intraday_data = intraday_start_time = intraday_end_time = avg_intraday_range = avg_intraday_range_by_day = None
    bullish_fvgs = []
    bearish_fvgs = []

    if intraday_choice == 'yes':
        intraday_start_time, intraday_end_time = user_input.get_intraday_times()
        result = get_data.get_intraday_data(ticker_input, start_date, end_date, intraday_start_time, intraday_end_time)
        
        if result is None:
            intraday_data = intraday_start_time = intraday_end_time = avg_intraday_range = avg_intraday_range_by_day = None
        else:
            intraday_data, full_day_data = result
            
            if intraday_data is None or full_day_data is None:
                intraday_data = intraday_start_time = intraday_end_time = avg_intraday_range = avg_intraday_range_by_day = None
            else:
                intraday_data = calc.filter_trading_days(intraday_data, start_date, end_date)
                full_day_data = calc.filter_trading_days(full_day_data, start_date, end_date)
                
                bullish_fvgs = get_data.check_intraday_bullish_fvgs(full_day_data)
                bearish_fvgs = get_data.check_intraday_bearish_fvgs(full_day_data)
                intraday_hod_lod_df = get_data.find_intraday_hod_lod_times(intraday_data)
                intraday_data, avg_intraday_range, intraday_ranges = calc.calculate_avg_intraday_range(intraday_data)   
                avg_intraday_range_by_day, intraday_range_by_day = calc.calculate_avg_intraday_range_by_day(intraday_data, daily_data)
                median_intraday_range = calc.calculate_median_intraday_range(intraday_ranges)
                median_intraday_range_by_day = calc.calculate_median_intraday_range_by_day(intraday_range_by_day)
                calc.calculate_median_bearish_reversal_time(intraday_hod_lod_df)
                calc.calculate_median_bullish_reversal_time(intraday_hod_lod_df)

    avg_daily_range, daily_ranges = calc.calculate_avg_dr(daily_data)
    avg_dr_by_day, dr_by_day = calc.calculate_avg_dr_by_day(daily_data)
    median_dr = calc.calculate_median_dr(daily_ranges)
    median_dr_by_day = calc.calculate_median_dr_by_day(dr_by_day)

    if intraday_choice == 'no' or intraday_data is None:
        median_intraday_range_by_day = None
        median_intraday_range = None

    print("\nDisplaying charts...")
    display_data.display_charts(avg_dr_by_day, time_input, lookback_input, ticker_input, avg_daily_range, avg_intraday_range_by_day, intraday_data, intraday_start_time, intraday_end_time, median_dr, median_dr_by_day, median_intraday_range_by_day)
    
    if intraday_data is not None:
        bt.run_backtest(intraday_data, bullish_fvgs, bearish_fvgs)
    else:
        print("Skipping backtest: No intraday data available.")

if __name__ == '__main__':
    main()