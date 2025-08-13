import yfinance as yf
import pandas as pd
import os
import numpy as np
from supabase import create_client
from datetime import datetime, timedelta, timezone
from config import AppSettings, OptionType

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
print("Supabase client initialized.")

def get_possible_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tickers = pd.read_html(url)[0]["Symbol"].str.replace(".", "-", regex=False).to_list()
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

    calls["option_type"] = OptionType.CALL.value
    puts["option_type"] = OptionType.PUT.value
    df = pd.concat([calls, puts], ignore_index=True)

    df["ticker"] = ticker
    df["expiry"] = expiry
    df["snapshot_date"] = datetime.now(timezone.utc).date().isoformat()

    df = df[[
        "contractSymbol", "ticker", "option_type", "strike", 
        "expiry", "bid", "ask", 
        "volume", "impliedVolatility", "snapshot_date"
    ]]

    df["volume"] = df["volume"].fillna(0).astype(int)
    df["open_interest"] = df["open_interest"].fillna(0)
    df["bid"] = df["bid"].fillna(0)
    df["ask"] = df["ask"].fillna(0)

    print(f"Formatted option data for {ticker} with {len(df)} rows.")
    return df

def upload_to_supabase(df, table_name="options_snapshot"):
    print(f"Uploading {len(df)} rows to Supabase table '{table_name}'...")
    records = df.to_dict(orient="records")
    supabase.table(table_name).insert(records).execute()
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
            if ticker == "AAPL" and df["ask"].sum() == 0: 
                print("holiday / weekend")
                # hardcoded "AAPL" because of it's reliability, no options will ever cost 0 in total
                # unless the data is corrupted - in that case, exit the entire upload process and wait for another day
                raise SystemExit("Invalid prices detected - exiting the program (probable holiday or weekend)")
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    print(f"\nTotal options rows collected: {len(all_options_df)}")
    supabase.table("options_snapshot").delete().neq("ticker", "").execute()
    if not all_options_df.empty:
        upload_to_supabase(all_options_df)
    else:
        print("No data to upload.")
    print("=== OPTIONS SNAPSHOT COMPLETE ===")