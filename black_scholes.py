import numpy as np
from scipy.stats import norm

def black_scholes_price(S, K, T, r, sigma, option_type = "Call"):

    # Parameters:

    # S - price of underlying asset (for example - stocks)
    # K - strike price of the option
    # T - time until maturity in years (with the assumption of an european option)
    # r - non-risk interest rate (used for discounting from T to t_0)
    # sigma - volatility of the underlying asset

    S = np.array(S)

    d1 = (np.log(S / K) + (r + sigma**2 * 0.5) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "Call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "Put":
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be either 'Call' or 'Put'")

    return price

def compute_greeks(S, K, T, r, sigma, option_type = "Call", greek_returned = "All"):

    S, K, T, r, sigma = map(np.array, (S, K, T, r, sigma))

    d1 = (np.log(S / K) + (r + sigma**2 * 0.5) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "Call":
        delta = norm.cdf(d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * norm.cdf(d2))
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "Put":
        delta = norm.cdf(d1) - 1
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                 + r * K * np.exp(-r * T) * norm.cdf(-d2))
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T)

    greek_return_dict = {
        "Delta": delta,
        "Gamma": gamma,
        "Vega": vega / 100,
        "Theta": theta / 365,
        "Rho": rho / 100   
    }

    if greek_returned == "All":
        return greek_return_dict
    else:
        return greek_return_dict[greek_returned]