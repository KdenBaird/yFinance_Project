# Trading Strategy Backtest Project

This project implements a backtesting engine for a trading strategy that utilizes Fair Value Gaps (FVGs) to place trades. The strategy checks for bullish and bearish FVGs and places buy or sell trades based on the closing price conditions within a specific trading window (9:50 AM - 11:10 AM). The backtest runs on historical stock data and is capable of dynamically adjusting stop-loss (SL) and take-profit (TP) levels based on market conditions.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Trading Strategy](#trading-strategy)
- [Futre Implementation](#future-implementation)

## Overview

This backtesting engine simulates trades based on identified bullish and bearish Fair Value Gaps (FVGs). It allows traders to test strategies that react to price gaps in the market, invalidating gaps that are closed before the defined trading window and executing trades when certain conditions are met during the trading window.

## Features

- **FVG Detection**: Automatically detects bullish and bearish FVGs.
- **FVG Invalidation**: FVGs are invalidated if price closes above/below certain thresholds before 9:50 AM.
- **Dynamic Trade Execution**: Trades are placed within the trading window if price conditions meet predefined criteria.
- **Adjustable SL/TP**: Take profit and stop loss levels are dynamically adjusted based on the market.
- **Backtesting**: Evaluate the performance of the trading strategy on historical data.

## Requirements

- Python 3.8+
- Pandas
- Numpy
- Yfinance (for downloading historical stock data)
- Matplotlib (optional, for graphing)
- [Backtesting](https://kernc.github.io/backtesting.py/) 

## Installation

First, clone this repository to your local machine:
"git clone: https://github.com/cjbaird1/yFinance_Project"

Install the required libraries by running in your terminal:

- Pandas:      "pip install pandas"
- Numpy:       "pip install numpy"
- YFinance:    "pip install yfinance"
- Matplotlib:  "pip install matplotlib"
- Backtesting: "pip install backtesting"

## Project Structure

- backtest.py        # Contains the main backtesting logic (unfinished)
- calculations.py    # Helper functions for calculating averages, medians, and other metrics for daily and intraday data
- display_data.py    # Logic for displaying calculations both to the terminal and to create and display charts
- dynamic_tpsl.py    # Dynamically adjusts take-profit and stop-loss levels based on specific market conditions (unfinished)
- get_data.py        # Fetches historical daily and intraday data using yfinance API.
- graphs.py          # Handles plotting and graphing of data (uses Matplotlib)
- README.md          # Project documentation

## Trading Strategy

This project implements an algorithmic trading strategy that operates during a defined time window of **9:50 AM to 11:10 AM**. The strategy focuses on identifying **Fair Value Gaps (FVGs)** and takes trades based on their formation and invalidation. Below is a detailed description of the strategy's logic:

### Strategy Overview

1. **Trading Window**:  
   Trades are only executed between **9:50 AM** and **11:10 AM** (Eastern Time). Outside of this window, no trades will be placed.

2. **Fair Value Gaps (FVGs)**:
   - **Bullish Fair Value Gap (FVG)**: Three candlestick pattern that could indicate bullish momentum. The gap between the first candle's high and the third candle's low.
   - **Bearish Fair Value Gap (FVG)**: Three candlestick pattern that could indicate bearish momentum. The gap between the first candle's low and the third candle's high.

3. **Invalidation Logic**:
   - FVGs formed between **00:00 and 9:50 AM** are invalidated if any candle before **9:50 AM** closes above (for bearish FVG) or below (for bullish FVG) the respective threshold. This ensures that only active FVGs during the trading window are considered valid.
   
4. **Trade Placement**:
   - **Buy Condition**: When a 5-minute candle closes above a bearish FVG within the trading window, a **buy** signal is placed on candle close.
   - **Sell Condition**: When a 5-minute candle closes below a bullish FVG within the trading window, a **sell** signal is placed on candle close.

5. **Risk Management**:
   The strategy includes dynamic stop-loss and take-profit levels, adjusted based on the time the trade is placed and the day of the week. This aims to optimize profit potential while managing risk effectively.

### Example

- **Buy Signal Example**:
   - A bullish FVG forms at **10:00 AM**
   - If a 5-minute candle closes below this FVG by **10:05 AM**, the strategy will place a **sell** order.
   
- **Sell Signal Example**:
   - A bearish FVG forms at **09:30 AM**
   - If a candle closes above the FVG at **10:20 AM**, the strategy will place a **buy** order so long as this fvg has not yet been invalidated.

## Future Implementation

This project is an ongoing effort to refine and optimize the algorithmic trading strategy. Below are some areas of improvement and features that I plan to implement in future versions:


1. **Incorporate Machine Learning Models**:
   - I'm currently taking a machine learning class (10/24), and would like to evaluate if I would be able to create predictive models by trianing and testing the data.

2. **Add Additional Time Frames**:
   - Currently the YFinance API can only give up to 50 days of intraday_data, 5m, 15m, 1h, etc. My live trading strategy is on the 1m time frame, so I'd like to evaluate other time frames and find a way around this.

3. **Optimize Performance for Real-Time Trading**:
   - Work on optimizing the performance of the algorithm for **real-time execution**, ensuring minimal delay between signal generation and trade placement.

4. **Backtest with Larger Data Sets**:
   - Perform backtests using **larger historical data sets** across different market conditions and time periods to further validate the strategy's robustness.

5. **Multi-Asset Support**:
   - Extend the strategy to trade multiple assets (stocks, futures, forex), allowing for **diversification** and greater adaptability to various market conditions. (I'm currently doing this, but there are some bugs.)

6. **Identify Seasonal Tendencies**:
   - I would like to draw conclusions based on how price moves in certain asset classes  based on the time of the year.

8. **Advanced Visualizations**:
   - Currently, I'm only using matplotlib to create histograms. I would like to advance this further and potentially have the functionality to compare and display multiple different asset classes.


