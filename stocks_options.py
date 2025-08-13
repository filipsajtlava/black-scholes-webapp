import pandas as pd
import yfinance as yf
import streamlit as st
import numpy as np
from datetime import datetime, timedelta
from config import OptionType

@st.cache_data
def get_stock_data(selected_ticker, selected_interval, config):
    df = yf.download(selected_ticker,
                     interval=selected_interval,
                     period=config.MAX_PERIODS[selected_interval]
                     )
    df = df.xs(selected_ticker, axis=1, level=1)
    return df

@st.cache_data
def get_tickers(_supabase_client):
    tickers = _supabase_client.rpc("get_unique_tickers").execute()
    return tickers.data

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

def get_options_data(selected_ticker, option_type, strike_price, supabase_client):
    options = supabase_client.rpc("get_options_by_ticker", {"ticker_text": selected_ticker}).execute()
    options_data = pd.DataFrame(options.data)

    if option_type in (OptionType.CALL.value, OptionType.PUT.value):
        options_data = options_data[options_data["option_type"] == option_type]
    else:
        raise ValueError("Please select one of the possible option types.")
    
    closest_expiry = options_data["expiry"]

    #closest_strike_index = abs(options_data["strike"] - strike_price).argmin()
    options_data = options_data.loc[:, 
                                    ["contractsymbol", "strike", "bid", "ask", "volume", "impliedvolatility"]
                                    ]
    options_data.columns = ["Contract symbol", "Strike price (K)", "Bid", "Ask", "Volume", "Implied volatility (IV)"]
    options_data = options_data.set_index("Contract symbol")

    #closest_expiry = closest_expiry.strftime("%d.%m.%Y")
    return options_data, closest_expiry

# EXPIRATION DATE FIX

# MAKE THE TABLE SMALLER?


    