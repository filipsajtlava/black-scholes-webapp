import numpy as np
from scipy.stats import norm
from config import OptionType

class EuropeanOption:
    def __init__(self, S, K, T, r, sigma, option_type):
        self.S = np.array(S)
        self.K = np.array(K)
        self.T = np.array(T)
        self.r = np.array(r)
        self.sigma = np.array(sigma)
        self.option_type = np.array(option_type)

    def calculate_d1_d2(self):
        d1 = (np.log(self.S / self.K) + (self.r + self.sigma**2 * 0.5) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        return d1, d2

    def bs_price(self):
        d1, d2 = self.calculate_d1_d2()

        if self.option_type == OptionType.CALL.value:
            price = self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        elif self.option_type == OptionType.PUT.value:
            price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        return price
    
    def bs_greeks(self, greek_to_return="All"):
        d1, d2 = self.calculate_d1_d2()
        if self.option_type == OptionType.CALL.value:
            delta = norm.cdf(d1)
            theta = (-self.S * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.T))
                    - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2))
            rho = self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2)
        elif self.option_type == OptionType.PUT.value:
            delta = norm.cdf(d1) - 1
            theta = (-self.S * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.T))
                    + self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2))
            rho = -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2)
        else:
            raise ValueError(f"option_type is different")

        gamma = norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))
        vega = self.S * norm.pdf(d1) * np.sqrt(self.T)

        greek_return_dict = {
            "Delta": delta,
            "Gamma": gamma,
            "Vega": vega / 100,
            "Theta": theta / 365,
            "Rho": rho / 100   
        }

        if greek_to_return == "All":
            return greek_return_dict
        else:
            try:
                return greek_return_dict[greek_to_return]
            except:
                raise ValueError("Invalid greek selection")
            
    def mc_generate_paths(self, paths, steps, seed):
        paths = int(paths)
        steps = int(steps)
        np.random.seed(seed)

        dt = self.T / steps
        Z = np.random.randn(paths, steps)
        increments = (self.r - 0.5 * self.sigma**2) * dt + self.sigma * np.sqrt(dt) * Z
        log_S = np.cumsum(increments, axis=1)
        log_S = np.hstack((np.zeros((paths, 1)), log_S))
        S_paths = self.S * np.exp(log_S)

        return S_paths

    def mc_model(self, paths, steps, seed, include_ci=True, alpha = 0.05):
        S_paths = self.mc_generate_paths(paths, steps, seed)
        last_column = S_paths[:, -1]

        if self.option_type == OptionType.CALL.value:
            payoffs = np.maximum(last_column - self.K, 0)
        elif self.option_type == OptionType.PUT.value:
            payoffs = np.maximum(self.K - last_column, 0)

        discounted_payoff = np.exp(-self.r * self.T) * payoffs
        price_estimate = np.mean(discounted_payoff)

        output = {"price": price_estimate}
        if include_ci:
            std_error = np.std(discounted_payoff, ddof=1) / np.sqrt(len(payoffs))
            z_score = norm.ppf(1 - alpha / 2)

            confidence_interval = [price_estimate - std_error * z_score, price_estimate + std_error * z_score] 
            confidence_interval = [round(val, 2) for val in confidence_interval]
            output["confidence_interval"] = confidence_interval

        return output