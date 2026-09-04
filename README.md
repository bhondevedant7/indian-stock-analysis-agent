# Indian Stock Analysis Agent

A Python-based Indian stock research agent for NSE/BSE stocks.

The project accepts an NSE stock symbol, such as `RELIANCE`, `TCS`, or `INFY`, downloads available market data, and creates an explainable research report. The report includes price trend, moving averages, RSI momentum, volatility, drawdown, and a Bullish, Neutral, or Bearish research view.

## Features

- Analyse one NSE stock at a time
- Automatic `.NS` suffix handling for NSE symbols
- 20-day and 50-day moving averages
- 14-day RSI momentum indicator
- Annualised volatility calculation
- Drawdown from the recent 52-week high
- Basic company information when available
- Explainable Bullish, Neutral, or Bearish research view
- Risk notes with every report
- Optional watchlist support for analysing multiple stocks

## Technologies Used

- Python
- yfinance
- pandas
- numpy
- PyCharm

## Installation

Clone or download this repository, then open the project folder in a terminal.

Install the required libraries:

```powershell
python -m pip install -r requirements.txt
```

## How to Run

Run the main program:

```powershell
python stock_agent.py
```

The program will ask for an NSE stock symbol.

Example:

```text
Enter an NSE stock symbol (example: RELIANCE): RELIANCE
```

You can also run the program with a stock symbol directly:

```powershell
python stock_agent.py RELIANCE
```

For other stocks:

```powershell
python stock_agent.py TCS
python stock_agent.py INFY
python stock_agent.py HDFCBANK
```

## Example Output

The agent provides information such as:

- Company name and NSE symbol
- Latest closing price
- 20-day and 50-day moving averages
- RSI value
- Volatility
- Drawdown from the 52-week high
- Bullish, Neutral, or Bearish research view
- Reasons behind the research view
- Risk note

## Disclaimer

This project is created for educational and research purposes only. It is not financial advice, investment advice, or a recommendation to buy, sell, or hold any stock.

Market data may be delayed, incomplete, or unavailable. Technical indicators do not guarantee future price movements. Always conduct independent research and consult a qualified financial advisor before making investment decisions.

This project does not connect to a broker, execute trades, or manage real money.

## Future Improvements

- Interactive charts and dashboard
- Fundamental analysis and financial ratios
- NSE/BSE announcements and corporate filing analysis
- News and sentiment analysis
- Historical backtesting
- Portfolio tracking
- Paper-trading simulation
- AI-generated summaries based on verified data

## Author

Created as a finance-focused startup project to explore Python, financial data analysis, automation, and explainable stock research.
