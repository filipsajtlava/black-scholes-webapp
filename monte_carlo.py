import numpy as np
import streamlit as st
from scipy.stats import norm
from config import OptionType

@st.cache_data
def simulate_gbm_paths(S, T, r, sigma, paths, steps, seed):
    
    np.random.seed(seed)

    # For clarity
    num_paths = paths
    num_steps = steps

    num_paths = int(num_paths)
    num_steps = int(num_steps)

    dt = T / num_steps
    Z = np.random.randn(num_paths, num_steps)

    increments = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z

    log_S = np.cumsum(increments, axis=1)
    log_S = np.hstack((np.zeros((num_paths, 1)), log_S))

    S_out = S * np.exp(log_S)
    return S_out

def monte_carlo_estimate(S_paths, K, T, r, option_type, alpha = 0.05):
    n_steps = S_paths.shape[1] - 1

    last_column = S_paths[:, n_steps]

    if option_type == OptionType.CALL.value:
        payoffs = np.maximum(last_column - K, 0)
    else:
        payoffs = np.maximum(K - last_column, 0)

    discounted_payoff = np.exp(-r * T) * payoffs
    price_estimate = np.mean(discounted_payoff)

    std_error = np.std(discounted_payoff, ddof=1) / np.sqrt(len(payoffs))
    z_score = norm.ppf(1 - alpha / 2)

    confidence_interval = [price_estimate - std_error * z_score, price_estimate + std_error * z_score] 
    confidence_interval = [round(val, 2) for val in confidence_interval]

    return round(price_estimate, 2), confidence_interval

