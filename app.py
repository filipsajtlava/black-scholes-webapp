from pricing import black_scholes_price
import streamlit as st

st.title("Black-Scholes Option Pricing")

st.sidebar.header("Option Parameters")

S = st.sidebar.number_input("Stock price (S) in €", min_value=0.01, value=100.0, max_value=250.0, step = 5.0)
K = st.sidebar.number_input("Strike price (K) in €", min_value=0.01, value=100.0, max_value=250.0, step = 5.0)
T = st.sidebar.number_input("Time to maturity (T) in years", min_value=0.01, value=1.0, max_value=5.0, step = 0.05)
r = st.sidebar.number_input("Non-risk interest rate (r)", min_value=0.0, value=0.05, step = 0.01)
sigma = st.sidebar.number_input("Volatility (σ)", min_value=0.01, max_value=1.0, value=0.1, step = 0.01)
option_type = st.sidebar.selectbox("Option Type", ["Call", "Put"])

if st.button("Calculate option price"):
    price = black_scholes_price(S, K, T, r, sigma, option_type)
    st.success(f"{option_type} option price: {price:.2f}€")