class BaseInputConfig:
    def __init__(self, label, default, variable, input_type, **kwargs):
        self.label = label
        self.default = default
        self.variable = variable
        self.type = input_type

        for keys, values in kwargs.items():
            setattr(self, keys, values)

class NumericConfig(BaseInputConfig): pass
class SegmentedControlConfig(BaseInputConfig): pass

class AppSettings:

    # ==== Constants ====
    
    CURRENCY = "€"
    MAX_GBM_LINES = 50
    SEED_INTERVAL = [1, 10000]

    # ==== Main input configs ====

    FIX_INPUT_CONFIGS = {
        "S": NumericConfig(
            label=f"Asset price (S) in {CURRENCY}",
            min=1.0,
            max=250.0,
            default=100.0,
            step=1.0,
            variable="S",
            input_type="slider"
        ),

        "K": NumericConfig(
            label=f"Strike price (K) in {CURRENCY}",
            min=1.0,
            max=250.0,
            default=100.0,
            step=1.0,
            variable="K",
            input_type="slider"
        ),

        "T": NumericConfig(
            label="Time to maturity (T) in years",
            min=0.0,
            max=5.0,
            default=1.0,
            step=0.05,
            variable="T",
            input_type="number_input"
        ),

        "r": NumericConfig(
            label="Non-risk interest rate (r)",
            min=0.01,
            max=0.3,
            default=0.05,
            step=0.01,
            variable="r",
            input_type="number_input"
        ),

        "sigma": NumericConfig(
            label="Volatility (σ)",
            min=0.01,
            max=1.0,
            default=0.1,
            step=0.01,
            variable="sigma",
            input_type="number_input"
        ),
        
        "option_type": SegmentedControlConfig(
        label="Option_type",
        options=["Call", "Put"],
        default="Call",
        selection_mode="single",
        variable="option_type",
        input_type="segmented_control"
        )
    }

    # ==== Monte Carlo configs ====

    MC_INPUT_CONFIGS = {
        "paths": NumericConfig(
            label="Number of different paths",
            min=1.0,
            max=100000.0,
            default=10000.0,
            step=500.0,
            variable="paths",
            input_type="number_input"
        ),

        "steps": NumericConfig(
            label="Number of steps in a path",
            min=10.0,
            max=500.0,
            default=100.0,
            step=10.0,
            variable="steps",
            input_type="number_input"
        )
    }

    @classmethod
    def get_variables_by_type(cls, input_type):
        return [
            input_config.variable for input_config in cls.FIX_INPUT_CONFIGS.values()
            if input_config.type == input_type
        ]
    
class Colors:

    PAYOFF_AREAS = ["#E03C32", "#FFD301", "#7BB662"]
    PUT_CALL = ["#E03C32", "#7BB662"]
    SEAMLESS_GREY = "#595A70"
    