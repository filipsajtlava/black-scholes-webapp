import numpy as np

def simulate_gbm_paths(S, T, r, sigma, num_paths, num_steps):
    
    num_paths = int(num_paths)
    num_steps = int(num_steps)

    dt = T / num_steps
    Z = np.random.randn(num_paths, num_steps)

    increments = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z

    log_S = np.cumsum(increments, axis=1)
    log_S = np.hstack((np.zeros((num_paths, 1)), log_S))

    S_out = S * np.exp(log_S)
    return S_out