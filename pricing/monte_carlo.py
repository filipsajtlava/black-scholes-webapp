import numpy as np

def simulate_gbm_paths(S, T, r, sigma, paths, steps):
    
    dt = T / steps
    Z = np.random.randn(paths, steps)

    increments = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z

    log_S = np.cumsum(increments, axis=1)
    log_S = np.hstack((np.zeros((paths, 1)), log_S))

    S_out = S * np.exp(log_S)
    return S_out