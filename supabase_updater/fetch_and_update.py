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
print("Supabase client initialized.")

def get_possible_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tickers = pd.read_html(url)[0]["Symbol"].str.replace(".", "-", regex=True).to_list()
    print(f"Fetched {len(tickers)} tickers.")
    return tickers

def get_closest_expiry(expirations, days_to_expiry=AppSettings.MODELLED_OPTIONS_EXPIRY_DAYS):
    target_date = pd.to_datetime(datetime.now() + timedelta(days=days_to_expiry))
    closest_index = np.abs((expirations - target_date).total_seconds().to_numpy()).argmin()
    closest = str(expirations[closest_index].date())
    print(f"Closest expiry found: {closest}")
    return closest

def fetch_option_data(yf_ticker, ticker, expiry):
    chain = yf_ticker.option_chain(expiry)
    calls = chain.calls
    puts = chain.puts
    print(f" - {len(calls)} calls, {len(puts)} puts fetched.")

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
    print(f"Formatted option data for {ticker} with {len(df)} rows.")
    return df

def upload_to_supabase(df, table_name="options_snapshot"):
    print(f"Uploading {len(df)} rows to Supabase table '{table_name}'...")
    records = df.to_dict(orient="records")
    for i in range(0, len(records), 500):
        chunk = records[i:i+500]
        print(f"Inserting rows {i} to {i+len(chunk)}...")
        response = supabase.table(table_name).insert(chunk).execute()
        if response.get("error"):
            print("Error inserting chunk:", response["error"])
        else:
            print(f"Inserted chunk {i // 500 + 1} successfully.")
    print("Upload to Supabase complete.")

if __name__ == "__main__":
    print("=== OPTIONS SNAPSHOT START ===")
    tickers = get_possible_sp500_tickers()
    all_options_df = pd.DataFrame()

    for idx, ticker in enumerate(tickers):
        print(f"\n[{idx+1}/{len(tickers)}] Processing ticker: {ticker}")
        try:
            yf_ticker = yf.Ticker(ticker)
            expirations = pd.to_datetime(yf_ticker.options)
            if len(expirations) == 0:
                print(f"No expirations available for {ticker}. Skipping.")
                continue
            expiry = get_closest_expiry(expirations)
            df = fetch_option_data(yf_ticker, ticker, expiry)
            all_options_df = pd.concat([all_options_df, df], ignore_index=True)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    print(f"\nTotal options rows collected: {len(all_options_df)}")
    if not all_options_df.empty:
        upload_to_supabase(all_options_df)
    else:
        print("No data to upload.")
    print("=== OPTIONS SNAPSHOT COMPLETE ===")
