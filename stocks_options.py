import pandas as pd
import yfinance as yf
import streamlit as st
import numpy as np
from datetime import datetime, timedelta
from config import OptionType

def get_stock_data(selected_ticker, selected_interval, config):
    df = yf.download(selected_ticker,
                     interval=selected_interval,
                     period=config.MAX_PERIODS[selected_interval]
                     )
    df = df.xs(selected_ticker, axis=1, level=1)
    return df

@st.cache_data
def get_possible_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tickers = pd.read_html(url)[0]["Symbol"].str.replace(".", "-", regex=False).to_list()
    return tickers


def get_closest_expiry(yf_ticker, config):
    """
    Inputs: yf_ticker (cls), config (cls)
    Outputs: (datetime) closest expiration date of actual options to the selected amount of days
    """
    expirations = pd.to_datetime(yf_ticker.options)
    days_to_expiry = config.MODELLED_OPTIONS_EXPIRY_DAYS

    target_date = pd.to_datetime(datetime.now() + timedelta(days=days_to_expiry))
    closest_index = np.abs((expirations - target_date).total_seconds().to_numpy()).argmin()
    closest = expirations[closest_index].date()
    return closest

def get_options_data(selected_ticker, option_type, strike_price, config):
    yf_ticker = yf.Ticker(selected_ticker)
    closest_expiry = get_closest_expiry(yf_ticker=yf_ticker, config=config)
    chain = yf_ticker.option_chain(str(closest_expiry))

    if option_type == OptionType.CALL.value:
        options_data = chain.calls
    elif option_type == OptionType.PUT.value:
        options_data = chain.puts
    else:
        raise ValueError("Please select one of the possible option types.")

    closest_strike_index = abs(options_data["strike"] - strike_price).argmin()
    options_data = options_data.loc[(closest_strike_index - config.MODELLED_OPTIONS_AMOUNT):(closest_strike_index + config.MODELLED_OPTIONS_AMOUNT), 
                                    ["contractSymbol", "strike", "bid", "ask", "volume", "impliedVolatility"]
                                    ]
    options_data.columns = ["Contract symbol", "Strike price (K)", "Bid", "Ask", "Volume", "Implied volatility (IV)"]
    options_data = options_data.set_index("Contract symbol")

    closest_expiry = closest_expiry.strftime("%d.%m.%Y")
    return options_data, closest_expiry


    