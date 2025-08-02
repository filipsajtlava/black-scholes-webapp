import pandas as pd
import yfinance as yf

def get_stock_data(selected_ticker, selected_interval, config):
    selected_ticker = selected_ticker[0]

    df = yf.download(selected_ticker,
                     interval=selected_interval,
                     period=config.MAX_PERIODS[selected_interval]
                     )
    df = df.xs(selected_ticker, axis=1, level=1)
    return df

def get_possible_tickers():
    try:
        return pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0].loc[:,"Symbol"]
    except:
        raise ValueError("Error with tickers input list")