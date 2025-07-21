import numpy as np

def simulate_gbm_paths(S, T, r, sigma, num_paths, num_steps, seed):
    
    np.random.seed(seed)

    num_paths = int(num_paths)
    num_steps = int(num_steps)

    dt = T / num_steps
    Z = np.random.randn(num_paths, num_steps)

    increments = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z

    log_S = np.cumsum(increments, axis=1)
    log_S = np.hstack((np.zeros((num_paths, 1)), log_S))

    S_out = S * np.exp(log_S)
    return S_out

def monte_carlo_estimate(S_paths, K, T, r, option_type):
    n_steps = S_paths.shape[1] - 1

    last_column = S_paths[:, n_steps]

    if option_type == "Call":
        payoff = np.maximum(last_column - K, 0)
    else:
        payoff = np.maximum(K - last_column, 0)

    discounted_price = np.exp(-r * T) * np.mean(payoff)
    return round(discounted_price, 2)