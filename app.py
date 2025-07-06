from pricing import black_scholes_price
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotting import create_basic_option_graph

maximum_stock_value = 250.0
maximum_strike_value = 250.0

st.set_page_config(page_title="Option Pricing App", layout="wide")
tab1, tab2, tab3 = st.tabs(["Mathematical background", "Option price calculator", "3rd page"])

with tab1:
    st.title("The math behind the famous Black-Scholes formula")


with tab2:
    st.title("Black-Scholes Option Pricing")

    void1, params_slider, void2, output, void3 = st.columns([0.5, 1.5, 1, 1.5, 1])

    with params_slider:
        st.subheader("Parameters")

        S = st.slider("Stock price (S) in €", min_value=1.0, value=100.0, max_value=maximum_stock_value, step = 1.0)
        K = st.slider("Strike price (K) in €", min_value=1.0, value=100.0, max_value=maximum_strike_value, step=1.0)
        T = st.number_input("Time to maturity (T) in years", min_value=0.01, value=1.0, max_value=5.0, step=0.05)
        r = st.number_input("Non-risk interest rate (r)", min_value=0.0, value=0.05, step=0.01)
        sigma = st.number_input("Volatility (σ)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
        option_type = st.selectbox("Option Type", ["Call", "Put"])

    with output:
        st.subheader("Option Price")
        price = black_scholes_price(S, K, T, r, sigma, option_type)
        st.success(f"{option_type} option price: {price:.2f}€")
        st.plotly_chart(create_basic_option_graph(S, K, maximum_stock_value, maximum_strike_value, price, option_type))