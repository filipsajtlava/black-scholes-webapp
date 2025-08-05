import plotly.graph_objects as go
import pandas as pd
from config import CandlestickInterval

def add_weekend_line(fig, df):
    difference = pd.Timedelta("1d")

    time_diffs = df.index.to_series().diff()
    gap_indexes = df.index[time_diffs > difference] # if difference in time is higher than 1 day - only true for weekends

    for gap_index in gap_indexes:
        fig.add_vline(
            x=gap_index,
            line_width=1,   
            line_dash="dash",
            line_color="gray",
            opacity=0.25
        )

        fig.add_annotation(
            x=gap_index,
            yref="paper",
            text="Weekend",
            showarrow=False,
            font=dict(color="gray")
        )

def plot_candlestick_asset(df, selected_interval, color_config):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        close=df["Close"],
        high=df["High"],
        low=df["Low"],
        increasing_line_color=color_config.GREEN,
        decreasing_line_color=color_config.RED
    ))

    if selected_interval in (CandlestickInterval.MINUTE.value, CandlestickInterval.HOUR.value):
        fig.update_xaxes(   
        rangebreaks=[
            dict(bounds=[20,13.5], pattern="hour"),
            dict(bounds=["sat", "mon"]),  # hide weekends
        ]
        )
        if selected_interval == CandlestickInterval.HOUR.value:
            add_weekend_line(fig, df)
    elif selected_interval == CandlestickInterval.DAY.value:
        fig.update_xaxes(   
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
        ]
        )  
        
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        height=450,
        showlegend=False,
        xaxis=dict(
            tickformat="%Y-%m-%d\n%H:%M" if "m" in selected_interval else "%Y-%m-%d",
            tickangle=45,
            #rangeslider=dict(visible=False),
        ),
        uirevision="candlestick"
    )
    return fig

