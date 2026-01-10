from backtesting import Backtest, Strategy
import pandas as pd
import backtesting

class fiveMinFVG(Strategy):
    bullish_fvgs = []
    bearish_fvgs = []

    def init(self):
        self.last_trade_date = None
        self.invalidation_checked_date = None
        self.entry_info = {}  # Store entry info for each trade
        self.current_entry_info = None  # Store entry info for the current open position
        
        # Determine trading window from the full dataset (available in init)
        df = self.data.df
        if len(df) > 0:
            times = pd.Series([idx.time() for idx in df.index])
            self.start_time = times.min()
            self.end_time = times.max()
        else:
            self.start_time = pd.Timestamp("09:30:00").time()
            self.end_time = pd.Timestamp("16:00:00").time()
        
        # Copy FVGs from class variables to instance variables
        self.bullish_fvgs = list(fiveMinFVG.bullish_fvgs) if fiveMinFVG.bullish_fvgs else []
        self.bearish_fvgs = list(fiveMinFVG.bearish_fvgs) if fiveMinFVG.bearish_fvgs else []
    
    def on_trade_close(self, trade):
        """Called when a trade is closed (TP, SL, or manual close)"""
        exit_time = self.data.index[-1].time()
        exit_price = self.data.Close[-1]
        exit_date = self.data.index[-1].date()
        pnl = trade.pl
        is_winner = pnl > 0
        
        result = "WINNER" if is_winner else "LOSER"
        
        # Get entry info from current_entry_info if available
        if self.current_entry_info:
            entry_time_str = self.current_entry_info['entry_time']
            entry_price_str = f"{self.current_entry_info['entry_price']:.2f}"
        else:
            entry_time_str = "N/A"
            entry_price_str = "N/A"
        
        print(f"[TRADE CLOSED] {result} - Exit Time: {exit_time}, Exit Price: {exit_price:.2f}, Exit Date: {exit_date}")
        print(f"  Entry Time: {entry_time_str}, Entry Price: {entry_price_str}")
        print(f"  P&L: ${pnl:.2f}")
        
        # Clean up entry info
        self.current_entry_info = None
        
    def next(self): 

        df = self.data.df
        
        if len(self.data) < 2:
            return
            
        current_time = self.data.index[-1].time()
        current_close = self.data.Close[-1]
        current_datetime = self.data.index[-1]
        current_open = self.data.Open[-1]
        prev_close = self.data.Close[-2] if len(self.data) >= 2 else current_close
        prev_open = self.data.Open[-2] if len(self.data) >= 2 else current_open
        current_date = current_datetime.date()
        
        # Check if this is the last candle in the dataset (exact match, not >=)
        is_last_candle = current_datetime == df.index[-1]

        if self.position is None and current_date != self.last_trade_date:
            self.last_trade_date = None
            self.current_entry_info = None  # Clear entry info when position closes
        
        # Close position at end of trading window OR at the very last candle of the dataset
        if self.position and (current_time >= self.end_time or is_last_candle):
            # Store exit info before closing
            exit_time = current_time
            exit_price = current_close
            pnl = self.position.pl
            is_winner = pnl > 0
            result = "WINNER" if is_winner else "LOSER"
            
            # Get entry info if available
            if self.current_entry_info:
                entry_time_str = self.current_entry_info['entry_time']
                entry_price_str = f"{self.current_entry_info['entry_price']:.2f}"
            else:
                entry_time_str = "N/A"
                entry_price_str = "N/A"
            
            self.position.close()
            close_reason = "END OF DAY" if current_time >= self.end_time and not is_last_candle else "END OF DATASET"
            print(f"[{close_reason}] {result} - Closed position at {exit_time} on {current_date}")
            print(f"  Entry Time: {entry_time_str}, Entry Price: {entry_price_str}")
            print(f"  Exit Time: {exit_time}, Exit Price: {exit_price:.2f}")
            print(f"  P&L: ${pnl:.2f}")
            self.current_entry_info = None  # Clear after closing
        
        if self.start_time <= current_time <= self.end_time:
            if current_date != self.invalidation_checked_date:
                start_time_ts = pd.Timestamp(f"{current_date} {self.start_time}").tz_localize('America/New_York')
                
                for fvg in self.bearish_fvgs[:]:
                    fvg_datetime = fvg['Datetime']
                    if hasattr(fvg_datetime, 'tz_localize') or hasattr(fvg_datetime, 'tz_convert'):
                        if fvg_datetime.tzinfo is None:
                            fvg_datetime = fvg_datetime.tz_localize('America/New_York')
                        elif fvg_datetime.tzinfo != start_time_ts.tzinfo:
                            fvg_datetime = fvg_datetime.tz_convert('America/New_York')
                    
                    if fvg_datetime.date() == current_date and fvg_datetime < start_time_ts:
                        try:
                            relevant_data = df.loc[fvg_datetime:start_time_ts, 'Close']
                            if len(relevant_data) > 0:
                                invalidated = (relevant_data > fvg['First Candle Low']).any()
                                if invalidated:
                                    self.bearish_fvgs.remove(fvg)
                        except Exception:
                            continue

                for fvg in self.bullish_fvgs[:]:
                    fvg_datetime = fvg['Datetime']
                    if hasattr(fvg_datetime, 'tz_localize') or hasattr(fvg_datetime, 'tz_convert'):
                        if fvg_datetime.tzinfo is None:
                            fvg_datetime = fvg_datetime.tz_localize('America/New_York')
                        elif fvg_datetime.tzinfo != start_time_ts.tzinfo:
                            fvg_datetime = fvg_datetime.tz_convert('America/New_York')
                    
                    if fvg_datetime.date() == current_date and fvg_datetime < start_time_ts:
                        try:
                            relevant_data = df.loc[fvg_datetime:start_time_ts, 'Close']
                            if len(relevant_data) > 0:
                                invalidated = (relevant_data < fvg['First Candle High']).any()
                                if invalidated:
                                    self.bullish_fvgs.remove(fvg)
                        except Exception:
                            continue
                
                self.invalidation_checked_date = current_date

            if not self.position:
                for fvg in self.bearish_fvgs[:]:
                    fvg_datetime = fvg['Datetime']
                    if hasattr(fvg_datetime, 'tz_localize'):
                        if fvg_datetime.tzinfo is None:
                            fvg_datetime = fvg_datetime.tz_localize('America/New_York')
                        if current_datetime.tzinfo is None:
                            current_datetime = current_datetime.tz_localize('America/New_York')
                        elif current_datetime.tzinfo != fvg_datetime.tzinfo:
                            current_datetime = current_datetime.tz_convert('America/New_York')
                            fvg_datetime = fvg_datetime.tz_convert('America/New_York')
                    
                    if current_datetime >= fvg_datetime and current_datetime.date() == fvg_datetime.date():
                        try:
                            start_time_ts = pd.Timestamp(f"{current_date} {self.start_time}").tz_localize('America/New_York')
                            if fvg_datetime < start_time_ts:
                                invalidated = False
                            else:
                                relevant_data = df.loc[fvg_datetime:current_datetime, 'Close']
                                invalidated = (relevant_data > fvg['First Candle Low']).any() if len(relevant_data) > 0 else False
                            
                            if current_date != self.last_trade_date and not invalidated and current_close > fvg['First Candle Low'] and current_close > current_open:
                                fvg_size = fvg.get('FVG Size', abs(fvg['Third Candle High'] - fvg['First Candle Low']))
                                
                                min_tp_sl = max(0.50, current_close * 0.005)
                                max_tp_sl = current_close * 0.10
                                
                                tp_distance = max(min_tp_sl, min(2 * fvg_size, max_tp_sl))
                                sl_distance = max(min_tp_sl, min(1 * fvg_size, max_tp_sl))
                                
                                long_tp_price = current_close + tp_distance
                                long_sl_price = current_close - sl_distance
                                
                                if long_tp_price > long_sl_price and long_tp_price > current_close:
                                    # Store entry info BEFORE opening the position
                                    self.current_entry_info = {
                                        'entry_time': current_time,
                                        'entry_price': current_close,
                                        'entry_date': current_date,
                                        'direction': 'BUY'
                                    }
                                    
                                    self.buy(sl=long_sl_price, tp=long_tp_price)
                                    print(f"\n[BUY SIGNAL] Time: {current_time}, Price: {current_close:.2f}")
                                    print(f"  Bearish FVG: Created at {fvg_datetime}, FVG Size: {fvg_size:.2f}")
                                    print(f"  Entry: {current_close:.2f}, TP: {long_tp_price:.2f} (+{tp_distance:.2f}), SL: {long_sl_price:.2f} (-{sl_distance:.2f})")
                                    
                                    self.bearish_fvgs.remove(fvg)
                                    self.last_trade_date = current_date
                                    break
                                else:
                                    if len(self.data) <= 10:
                                        print(f"[WARNING] Invalid TP/SL for BUY: TP={long_tp_price:.2f}, SL={long_sl_price:.2f}, Entry={current_close:.2f}")
                        except Exception as e:
                            print(f"Error evaluating bearish FVG for trade: {e}")
                            continue

                for fvg in self.bullish_fvgs[:]:
                    fvg_datetime = fvg['Datetime']
                    if hasattr(fvg_datetime, 'tz_localize'):
                        if fvg_datetime.tzinfo is None:
                            fvg_datetime = fvg_datetime.tz_localize('America/New_York')
                        if current_datetime.tzinfo is None:
                            current_datetime = current_datetime.tz_localize('America/New_York')
                        elif current_datetime.tzinfo != fvg_datetime.tzinfo:
                            current_datetime = current_datetime.tz_convert('America/New_York')
                            fvg_datetime = fvg_datetime.tz_convert('America/New_York')
                    
                    if current_datetime >= fvg_datetime and current_datetime.date() == fvg_datetime.date():
                        try:
                            start_time_ts = pd.Timestamp(f"{current_date} {self.start_time}").tz_localize('America/New_York')
                            if fvg_datetime < start_time_ts:
                                invalidated = False
                            else:
                                relevant_data = df.loc[fvg_datetime:current_datetime, 'Close']
                                invalidated = (relevant_data < fvg['First Candle High']).any() if len(relevant_data) > 0 else False
                            
                            if current_date != self.last_trade_date and not invalidated and current_close < fvg['First Candle High'] and current_close < current_open:
                                fvg_size = fvg.get('FVG Size', abs(fvg['Third Candle Low'] - fvg['First Candle High']))
                                
                                min_tp_sl = max(0.50, current_close * 0.005)
                                max_tp_sl = current_close * 0.10
                                
                                tp_distance = max(min_tp_sl, min(2 * fvg_size, max_tp_sl))
                                sl_distance = max(min_tp_sl, min(1 * fvg_size, max_tp_sl))
                                
                                short_tp_price = current_close - tp_distance
                                short_sl_price = current_close + sl_distance
                                
                                if short_tp_price < short_sl_price and short_tp_price < current_close:
                                    # Store entry info BEFORE opening the position
                                    self.current_entry_info = {
                                        'entry_time': current_time,
                                        'entry_price': current_close,
                                        'entry_date': current_date,
                                        'direction': 'SELL'
                                    }
                                    
                                    self.sell(sl=short_sl_price, tp=short_tp_price)
                                    print(f"\n[SELL SIGNAL] Time: {current_time}, Price: {current_close:.2f}")
                                    print(f"  Bullish FVG: Created at {fvg_datetime}, FVG Size: {fvg_size:.2f}")
                                    print(f"  Entry: {current_close:.2f}, TP: {short_tp_price:.2f} (-{tp_distance:.2f}), SL: {short_sl_price:.2f} (+{sl_distance:.2f})")
                                    
                                    self.bullish_fvgs.remove(fvg)
                                    self.last_trade_date = current_date
                                    break
                                else:
                                    if len(self.data) <= 10:
                                        print(f"[WARNING] Invalid TP/SL for SELL: TP={short_tp_price:.2f}, SL={short_sl_price:.2f}, Entry={current_close:.2f}")
                        except Exception as e:
                            print(f"Error evaluating bullish FVG for trade: {e}")
                            continue


def run_backtest(intraday_data, bullish_fvgs, bearish_fvgs):
    fiveMinFVG.bullish_fvgs = bullish_fvgs.copy() if bullish_fvgs else []
    fiveMinFVG.bearish_fvgs = bearish_fvgs.copy() if bearish_fvgs else []

    bt = Backtest(intraday_data, fiveMinFVG, cash=100_000, finalize_trades=True)
    stats = bt.run()
    print(f"\n{'='*60}")
    print("BACKTEST RESULTS")
    print(f"{'='*60}")
    print(f"Start:                     {stats['Start']}")
    print(f"End:                       {stats['End']}")
    print(f"Duration:                   {stats['Duration']}")
    print(f"Exposure Time [%]:          {stats['Exposure Time [%]']:.2f}")
    print(f"Equity Final [$]:           {stats['Equity Final [$]']:.2f}")
    print(f"Equity Peak [$]:            {stats['Equity Peak [$]']:.2f}")
    print(f"Return [%]:                 {stats['Return [%]']:.2f}")
    print(f"Buy & Hold Return [%]:     {stats['Buy & Hold Return [%]']:.2f}")
    print(f"Return (Ann.) [%]:          {stats['Return (Ann.) [%]']:.2f}")
    print(f"Volatility (Ann.) [%]:     {stats['Volatility (Ann.) [%]']:.2f}")
    print(f"CAGR [%]:                   {stats['CAGR [%]']:.2f}")
    print(f"Sharpe Ratio:               {stats['Sharpe Ratio']:.2f}" if pd.notna(stats['Sharpe Ratio']) else "Sharpe Ratio:               NaN")
    print(f"Sortino Ratio:              {stats['Sortino Ratio']:.2f}" if pd.notna(stats['Sortino Ratio']) else "Sortino Ratio:              NaN")
    print(f"Calmar Ratio:               {stats['Calmar Ratio']:.2f}" if pd.notna(stats['Calmar Ratio']) else "Calmar Ratio:               NaN")
    print(f"Max. Drawdown [%]:          {stats['Max. Drawdown [%]']:.2f}")
    print(f"# Trades:                    {stats['# Trades']}")
    print(f"Win Rate [%]:               {stats['Win Rate [%]']:.2f}" if pd.notna(stats['Win Rate [%]']) else "Win Rate [%]:               NaN")
    print(f"Best Trade [%]:             {stats['Best Trade [%]']:.2f}" if pd.notna(stats['Best Trade [%]']) else "Best Trade [%]:             NaN")
    print(f"Worst Trade [%]:            {stats['Worst Trade [%]']:.2f}" if pd.notna(stats['Worst Trade [%]']) else "Worst Trade [%]:            NaN")
    print(f"Avg. Trade [%]:             {stats['Avg. Trade [%]']:.2f}" if pd.notna(stats['Avg. Trade [%]']) else "Avg. Trade [%]:             NaN")
    print(f"Profit Factor:              {stats['Profit Factor']:.2f}" if pd.notna(stats['Profit Factor']) else "Profit Factor:              NaN")
    print(f"{'='*60}\n")
   