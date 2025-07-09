class input_config:
    def __init__(self, label, min_val, max_val, default_val, step, variable):
        self.label = label
        self.min = min_val
        self.max = max_val
        self.default = default_val
        self.step = step
        self.variable = variable

asset_price_slider = input_config(
    label="Stock price (S) in €",
    min_val=1.0,
    max_val=250.0,
    default_val=100.0,
    step=1.0,
    variable="S"
)

strike_price_slider = input_config(
    label="Strike price (K) in €",
    min_val=1.0,
    max_val=250.0,
    default_val=100.0,
    step=1.0,
    variable="K"
)

time_input = input_config(
    label="Time to maturity (T) in years",
    min_val=0.0,
    max_val=5.0,
    default_val=1.0,
    step=0.05,
    variable="T"
)

non_risk_interest_input = input_config(
    label="Non-risk interest rate (r)",
    min_val=0.01,
    max_val=0.3,
    default_val=0.05,
    step=0.01,
    variable="r"
)

volatility_input = input_config(
    label="Volatility (σ)",
    min_val=0.01,
    max_val=1.0,
    default_val=0.1,
    step=0.01,
    variable="sigma"
)