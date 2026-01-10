# Trading Strategy Documentation

## Overview

This strategy is based on **Fair Value Gaps (FVGs)**, which are price gaps that occur when three consecutive candles create an imbalance in the market. The strategy trades on the assumption that these gaps will eventually be filled, and enters positions when price begins to move back into the gap.

## What is a Fair Value Gap (FVG)?

A Fair Value Gap is a price imbalance created by three consecutive candles:

### Bullish FVG
- **Definition**: A gap UP created when the first candle's low is higher than the third candle's high
- **Visual**: `[Candle 1 Low] > [Candle 3 High]` - creating a gap between them
- **Interpretation**: Price gapped up, leaving an unfilled area below
- **Trading Logic**: We SELL (short) when price moves back down into this gap

### Bearish FVG
- **Definition**: A gap DOWN created when the first candle's high is lower than the third candle's low
- **Visual**: `[Candle 1 High] < [Candle 3 Low]` - creating a gap between them
- **Interpretation**: Price gapped down, leaving an unfilled area above
- **Trading Logic**: We BUY (long) when price moves back up into this gap

## FVG Detection

### Detection Process
1. **Data Source**: Full trading day data (9:30 AM - 4:00 PM ET) is used for FVG detection
2. **Scanning**: The algorithm scans all 5-minute candles, grouping by trading day
3. **Sliding Window**: For each day, it checks every set of 3 consecutive candles
4. **Size Filter**: Only FVGs with a size greater than `MIN_FVG_SIZE` are considered valid

### Minimum FVG Size
- **Current Value**: `0.10` (10 cents)
- **Location**: `get_data.py` line 10: `MIN_FVG_SIZE = 0.10`
- **Purpose**: Filters out noise and very small gaps that may not be meaningful
- **Adjustment**: Increase for higher-priced stocks or more conservative trading, decrease for more opportunities

## FVG Invalidation

An FVG becomes invalid (and is removed from consideration) if price fills the gap before the trading window begins.

### Bearish FVG Invalidation
- **Condition**: If any closing price between the FVG creation time and the trading window start is **above** the FVG's "First Candle Low"
- **Logic**: If price already moved above the gap, the opportunity is gone
- **When Checked**: At the start of each new trading day

### Bullish FVG Invalidation
- **Condition**: If any closing price between the FVG creation time and the trading window start is **below** the FVG's "First Candle High"
- **Logic**: If price already moved below the gap, the opportunity is gone
- **When Checked**: At the start of each new trading day

## Trading Window

### Dynamic Window
- The trading window is automatically determined from the user's selected intraday time range
- **Example**: If you select 10:00 AM - 11:00 AM, the strategy only trades during that window
- **Purpose**: Allows you to focus on specific market hours (e.g., morning volatility, lunch lull, etc.)

### Trading Restrictions
- **Only trades when flat**: No new positions if already in a trade (`not self.position`)
- **One trade per day**: The `last_trade_date` check ensures only one trade per calendar day
- **Window enforcement**: Trades can only be placed during the specified time window

## Entry Signals

### BUY Signal (Bearish FVG)

A buy order is placed when **ALL** of the following conditions are met:

1. **FVG Exists**: A valid bearish FVG is in the list (not invalidated)
2. **Time Check**: Current datetime is >= FVG creation datetime, and it's the same trading day
3. **No Invalidation**: No closing prices between FVG creation and trading window start are above the FVG's "First Candle Low"
4. **Entry Trigger**:
   - `current_close > fvg['First Candle Low']` - Price has moved above the gap
   - `current_close > current_open` - Current candle is bullish (green)

**Execution**: Buy order placed at the **next candle's open price**

### SELL Signal (Bullish FVG)

A sell (short) order is placed when **ALL** of the following conditions are met:

1. **FVG Exists**: A valid bullish FVG is in the list (not invalidated)
2. **Time Check**: Current datetime is >= FVG creation datetime, and it's the same trading day
3. **No Invalidation**: No closing prices between FVG creation and trading window start are below the FVG's "First Candle High"
4. **Entry Trigger**:
   - `current_close < fvg['First Candle High']` - Price has moved below the gap
   - `current_close < current_open` - Current candle is bearish (red)

**Execution**: Sell order placed at the **next candle's open price**

## Risk Management

### Take Profit (TP) and Stop Loss (SL) Levels

TP/SL levels are **dynamically calculated** based on the **Fair Value Gap (FVG) size** that triggered the trade. This approach ensures that risk management scales appropriately with the size of the price gap, making the strategy adaptable across different asset classes and price levels.

#### Calculation Method

**For Bearish FVG (BUY signals)**:
- **FVG Size**: `Third Candle High - First Candle Low`
- **Take Profit**: `Entry Price + (2 × FVG Size)`
- **Stop Loss**: `Entry Price - (1 × FVG Size)`
- **Risk/Reward Ratio**: 2:1 (risk 1× FVG to make 2× FVG)

**For Bullish FVG (SELL signals)**:
- **FVG Size**: `First Candle Low - Third Candle High`
- **Take Profit**: `Entry Price - (2 × FVG Size)`
- **Stop Loss**: `Entry Price + (1 × FVG Size)`
- **Risk/Reward Ratio**: 2:1 (risk 1× FVG to make 2× FVG)

#### Safety Bounds

To prevent unrealistic TP/SL values, the strategy applies minimum and maximum bounds:

- **Minimum TP/SL**: `max($0.50, 0.5% of entry price)` - Prevents noise trades with tiny FVGs
- **Maximum TP/SL**: `10% of entry price` - Caps risk on extremely large FVGs

**Example Calculations**:

For a stock at $180 with an FVG size of $2.00:
- TP = $180 + (2 × $2.00) = **$184.00**
- SL = $180 - (1 × $2.00) = **$178.00**

For a stock at $180 with an FVG size of $0.10 (below minimum):
- Minimum = max($0.50, $180 × 0.005) = **$0.90**
- TP = $180 + $0.90 = **$180.90**
- SL = $180 - $0.90 = **$179.10**

#### Advantages of FVG-Based TP/SL

1. **Scales with Setup**: Larger gaps get wider TP/SL, smaller gaps get tighter TP/SL
2. **Asset-Agnostic**: Works for stocks at $15 (PLTR) or $500 (MSFT) without adjustment
3. **Context-Aware**: TP/SL is proportional to the actual price imbalance being traded
4. **Maintains Risk/Reward**: Consistent 2:1 ratio regardless of FVG size

#### Location in Code

TP/SL calculation is located in `backtest.py`:
- **Bearish FVG (BUY)**: Lines ~207-220
- **Bullish FVG (SELL)**: Lines ~260-273

#### Adjusting TP/SL Multipliers

To modify the TP/SL multipliers, edit `backtest.py`:

```python
# For Bearish FVG (BUY signals)
tp_distance = max(min_tp_sl, min(2 * fvg_size, max_tp_sl))  # Change 2 to desired multiplier
sl_distance = max(min_tp_sl, min(1 * fvg_size, max_tp_sl))  # Change 1 to desired multiplier

# For Bullish FVG (SELL signals) - same multipliers apply
```

**Considerations**:
- **Larger multipliers** (e.g., 3× for TP, 1.5× for SL): More room for price movement, but changes risk/reward ratio
- **Smaller multipliers** (e.g., 1.5× for TP, 0.75× for SL): Tighter risk control, but may reduce profitability
- **Minimum bounds**: Adjust `min_tp_sl` calculation to change the floor (currently $0.50 or 0.5%)
- **Maximum bounds**: Adjust `max_tp_sl` calculation to change the cap (currently 10% of entry price)

## Position Management

### One Trade Per Day
- **Mechanism**: `last_trade_date` tracks the date of the last trade
- **Purpose**: Prevents overtrading and ensures focus on quality setups
- **Location**: `backtest.py` line 26 (initialization) and lines 203, 242 (updates)

### Position Status Check
- **Check**: `if not self.position:` ensures we're flat before entering
- **Purpose**: Prevents adding to positions or entering conflicting trades
- **Location**: `backtest.py` line 177

### End-of-Day Exit
- **Mechanism**: All open positions are automatically closed at the end of the trading window
- **Purpose**: Prevents positions from staying open overnight and ensures capital is available for new trades
- **Location**: `backtest.py` lines 94-97
- **Note**: Positions close at the last candle of the trading window (e.g., 11:10:00 if window is 9:50-11:10)

## Strategy Flow

### Daily Reset (New Trading Day)
1. Check all FVGs for invalidation
2. Remove invalidated FVGs from consideration
3. Reset `last_trade_date` check

### For Each Candle (Within Trading Window)
1. Check if we're flat (`not self.position`)
2. Check if we haven't traded today (`current_date != self.last_trade_date`)
3. Evaluate bearish FVGs for BUY signals
4. Evaluate bullish FVGs for SELL signals
5. If signal found, place order and exit (only one trade per day)

## Configurable Parameters Summary

| Parameter | Current Value | Location | Description |
|-----------|--------------|----------|-------------|
| `MIN_FVG_SIZE` | 0.10 | `get_data.py:10` | Minimum gap size in dollars to consider FVG valid |
| `TP Multiplier` | 2× FVG Size | `backtest.py:209, 262` | Take profit = Entry ± (2 × FVG Size) |
| `SL Multiplier` | 1× FVG Size | `backtest.py:210, 263` | Stop loss = Entry ± (1 × FVG Size) |
| `Min TP/SL` | $0.50 or 0.5% | `backtest.py:211, 264` | Minimum TP/SL distance (prevents noise trades) |
| `Max TP/SL` | 10% of entry | `backtest.py:212, 265` | Maximum TP/SL distance (caps risk on large FVGs) |
| Trading Window | User-defined | `user_input.py` | Time range for trading (e.g., 10:00-11:00) |
| Initial Capital | $100,000 | `backtest.py:291` | Starting capital for backtest |

## Strategy Assumptions

1. **Gap Fill Theory**: FVGs represent imbalances that will eventually be filled
2. **Time Sensitivity**: FVGs are most actionable on the same day they're created
3. **Directional Bias**: Price moving into a gap with momentum (bullish/bearish candle) indicates continuation
4. **Market Hours**: Strategy works best during regular trading hours (9:30 AM - 4:00 PM ET)

## Limitations and Considerations

1. **Single Trade Per Day**: May miss multiple opportunities on volatile days
2. **FVG-Based TP/SL**: While adaptive, may still be too tight or too wide depending on market volatility
3. **No Trend Filter**: Doesn't consider overall market direction
4. **5-Minute Timeframe**: May be too fast for some market conditions
5. **FVG Size Threshold**: May filter out valid but smaller opportunities
6. **Minimum TP/SL Bounds**: Small FVGs may use minimum bounds instead of FVG-based calculation, potentially affecting risk/reward
7. **End-of-Day Exits**: Positions close at trading window end, which may cut profitable trades short or prevent losses from extending

## Future Enhancements

Potential improvements to consider:
- **ATR-based TP/SL**: Combine FVG size with Average True Range for volatility-adjusted risk management
- **Multiple trades per day**: Allow more than one trade per day with position sizing
- **Trend filter**: Only trade with the overall market trend (e.g., only longs in uptrends)
- **Volume confirmation**: Require volume confirmation for FVG entries
- **Trailing stops**: Implement trailing stop-loss to protect profits
- **Partial exits**: Take partial profits at 1× FVG size, let remainder run to 2× FVG size
- **Time-based TP/SL scaling**: Adjust TP/SL based on time remaining in trading window
- **FVG quality scoring**: Prioritize larger, more significant FVGs over smaller ones

