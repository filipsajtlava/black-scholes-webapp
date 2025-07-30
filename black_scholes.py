import numpy as np
from scipy.stats import norm
from config import OptionType, VariableKey

def calculate_d1_d2(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 * 0.5) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

def black_scholes_price(selected_parameters):
    try:
        S = selected_parameters[VariableKey.S.value]
        K = selected_parameters[VariableKey.K.value]
        T = selected_parameters[VariableKey.T.value]
        r = selected_parameters[VariableKey.R.value]
        sigma = selected_parameters[VariableKey.SIGMA.value]
        option_type = selected_parameters[VariableKey.OPTION_TYPE.value]
    except KeyError as error:
        raise ValueError(f"Missing variable in the list: {error}")  
    
    S = np.array(S)

    # Parameters:

    # S - price of underlying asset (for example - stocks)
    # K - strike price of the option
    # T - time until maturity in years (with the assumption of an european option)
    # r - non-risk interest rate (used for discounting from T to t_0)
    # sigma - volatility of the underlying asset
    d1, d2 = calculate_d1_d2(S, K, T, r, sigma)

    if option_type == OptionType.CALL.value:
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == OptionType.PUT.value:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError(f"option_type is different")

    return price

def compute_greeks(selected_parameters, greek_returned = "All"):
    try:
        S = selected_parameters[VariableKey.S.value]
        K = selected_parameters[VariableKey.K.value]
        T = selected_parameters[VariableKey.T.value]
        r = selected_parameters[VariableKey.R.value]
        sigma = selected_parameters[VariableKey.SIGMA.value]
        option_type = selected_parameters[VariableKey.OPTION_TYPE.value]
    except KeyError as error:
        raise ValueError(f"Missing variable in the list: {error}")  

    S, K, T, r, sigma = map(np.array, (S, K, T, r, sigma))

    d1, d2 = calculate_d1_d2(S, K, T, r, sigma)

    if option_type == OptionType.CALL.value:
        delta = norm.cdf(d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * norm.cdf(d2))
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == OptionType.PUT.value:
        delta = norm.cdf(d1) - 1
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                 + r * K * np.exp(-r * T) * norm.cdf(-d2))
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
    else:
        raise ValueError(f"option_type is different")

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
        try:
            return greek_return_dict[greek_returned]
        except:
            raise ValueError("Greek not in the dictionary")