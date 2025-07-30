import yfinance as yf
import plotly.graph_objects as go
from config import MAX_PERIODS

def plot_candlestick_asset(selected_ticker, selected_interval, config, color_config):
    df = yf.download(selected_ticker,
                     interval=selected_interval,
                     period=MAX_PERIODS[selected_interval]
                     )