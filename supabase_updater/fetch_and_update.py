import yfinance as yf
import os
import pandas as pd
import numpy as np
from supabase import create_client
from datetime import datetime, timedelta, timezone

from config import AppSettings

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_possible_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tickers = pd.read_html(url)[0]["Symbol"].str.replace(".", "-", regex=True).to_list()
    return tickers

def get_closest_expiry(expirations, days_to_expiry = AppSettings.MODELLED_OPTIONS_EXPIRY_DAYS):
    target_date = pd.to_datetime(datetime.now() + timedelta(days=days_to_expiry))
    closest_index = np.abs((expirations - target_date).total_seconds().to_numpy()).argmin()
    return str(expirations[closest_index].date())

def fetch_option_data(yf_ticker, ticker, expiry):
    calls = yf_ticker.option_chain(expiry).calls
    puts = yf_ticker.option_chain(expiry).puts

    calls["option_type"] = "call"
    puts["option_type"] = "put"
    df = pd.concat([calls, puts], ignore_index=True)

    df["ticker"] = ticker
    df["expiry"] = expiry
    df["snapshot_date"] = datetime.now(timezone.utc).date()

    df = df.rename(columns={
        "lastPrice": "last_price",
        "impliedVolatility": "implied_volatility",
        "openInterest": "open_interest"
    })
    df = df[[
        "ticker", "option_type", "strike", "expiry",
        "last_price", "bid", "ask", "implied_volatility",
        "volume", "open_interest", "snapshot_date"
    ]]

    return df

if __name__ == "__main__":
    tickers = get_possible_sp500_tickers()
    all_options_df = pd.DataFrame()

    for ticker in tickers:
        yf_ticker = yf.Ticker(ticker)
        expirations = pd.to_datetime(yf_ticker.options)
        if len(expirations) > 0:
            expiry = get_closest_expiry(expirations)
            df = fetch_option_data(yf_ticker, ticker, expiry)
            all_options_df = pd.concat([all_options_df, df], ignore_index=True)

# basically what needs to be done is fetching call and put option data for the specific expiry and after that we need
# to update the table in the database with the data (every xx:xx hours utilizing something from github - at like 24:00)

# also send the tickers that are going to be used into the database, maybe it's enough just to use the tickers 
# part from the main table in the database

# other than that just make the app fetch the data from there, and also make it so that the expiry of the option
# is showed in the app so that we are sure what we are using

# the keys are also an important part - the streamlit application can use the anon key which is read only,
# but for the updating of the table we need to use the special key that has to be in the .env

# this way the github-thingy will fetch the data using the .env key from a secure place to update the data every
# midnight and the streamlit application that's shared completely will only use an anon key
