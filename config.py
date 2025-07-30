from enum import Enum

class VariableKey(str, Enum): # define new variables / inputs through this it's more stable
    S = "Asset"
    K = "K"
    T = "T"
    R = "r"
    SIGMA = "sigma"
    OPTION_TYPE = "option_type"
    PATHS = "paths"
    STEPS = "steps"
    INTERVAL = "interval"

class StreamlitInputs(str, Enum): # also important to add the new type of selectors
    SLIDER = "slider"
    NUMBER_INPUT = "number_input"
    SEGMENTED_CONTROL = "segmented_control"

# ===========================
# ==== 'Fixed' constants ====
# ===========================

class OptionType(str, Enum):
    CALL = "Call"
    PUT = "Put"

class Greeks(str, Enum):
    DELTA = "Delta"
    GAMMA = "Gamma"
    VEGA = "Vega"
    THETA = "Theta"
    RHO = "Rho"

class CandlestickInterval(str, Enum):
    MINUTE = "1m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1wk"
    MONTH = "1mo"

MAX_PERIODS = {
    CandlestickInterval.MINUTE.value: "7d",
    CandlestickInterval.HOUR.value: "60d",
    CandlestickInterval.DAY.value: "max",
    CandlestickInterval.WEEK.value: "max",
    CandlestickInterval.MONTH.value: "max",
}

# =====================
# ==== Definitions ====
# =====================

class NumericSliderConfig:
    def __init__(self, label, min_value, max_value, default, step, variable, input_type):
            self.label = label
            self.min = min_value
            self.max = max_value
            self.default = default
            self.step = step
            self.variable = variable
            self.type = input_type

class SegmentedControlConfig:
    def __init__(self, label, options, default, selection_mode, variable):
        self.label = label
        self.options = options
        self.default = default
        self.selection_mode = selection_mode
        self.variable = variable
        self.type = "segmented_control"

# ==============================
# ==== 'Variable' constants ====
# ==============================

class AppSettings:
    
    CURRENCY = "€"
    MAX_GBM_LINES = 50
    SEED_INTERVAL = [1, 10000]

    # ============================
    # ==== Main input configs ====
    # ============================

    STREAMLIT_INPUT_CONFIGS = {
        VariableKey.S.value: NumericSliderConfig(
            label=f"Asset price (S) in {CURRENCY}",
            min_value=1.0,
            max_value=250.0,
            default=100.0,
            step=1.0,
            variable=VariableKey.S.value,
            input_type="slider"
        ),

        VariableKey.K.value: NumericSliderConfig(
            label=f"Strike price (K) in {CURRENCY}",
            min_value=1.0,
            max_value=250.0,
            default=100.0,
            step=1.0,
            variable=VariableKey.K.value,
            input_type="slider"
        ),

        VariableKey.T.value: NumericSliderConfig(
            label="Time to maturity (T) in years",
            min_value=0.0,
            max_value=5.0,
            default=1.0,
            step=0.05,
            variable=VariableKey.T.value,
            input_type="number_input"
        ),

        VariableKey.R.value: NumericSliderConfig(
            label="Non-risk interest rate (r)",
            min_value=0.01,
            max_value=0.3,
            default=0.05,
            step=0.01,
            variable=VariableKey.R.value,
            input_type="number_input"
        ),

        VariableKey.SIGMA.value: NumericSliderConfig(
            label="Volatility (σ)",
            min_value=0.01,
            max_value=1.0,
            default=0.1,
            step=0.01,
            variable=VariableKey.SIGMA.value,
            input_type="number_input"
        ),
        
        VariableKey.OPTION_TYPE.value: SegmentedControlConfig(
        label="Option type",
        options=[OptionType.CALL.value, OptionType.PUT.value],
        default=OptionType.CALL.value,
        selection_mode="single",
        variable=VariableKey.OPTION_TYPE.value
        ),

    # =============================
    # ==== Monte Carlo configs ====
    # =============================        

        VariableKey.PATHS.value: NumericSliderConfig(
            label="Number of different paths",
            min_value=1.0,
            max_value=100000.0,
            default=10000.0,
            step=500.0,
            variable=VariableKey.PATHS.value,
            input_type="number_input"
        ),

        VariableKey.STEPS.value: NumericSliderConfig(
            label="Number of steps in a path",
            min_value=10.0,
            max_value=500.0,
            default=100.0,
            step=10.0,
            variable=VariableKey.STEPS.value,
            input_type="number_input"
        ),

    # =============================
    # ==== Candlestick configs ====
    # =============================

        VariableKey.INTERVAL.value: SegmentedControlConfig(
            label="Select time interval",
            options=[interval.value for interval in CandlestickInterval],
            default=CandlestickInterval.DAY.value,
            selection_mode="single",
            variable=VariableKey.INTERVAL.value
            )
    }

    @classmethod
    def get_variables_by_type(cls, input_type):
        return [
            input_config.variable for input_config in cls.STREAMLIT_INPUT_CONFIGS.values()
            if input_config.type == input_type
        ]

class Colors:

    PAYOFF_AREAS = ["#E03C32", "#FFD301", "#7BB662"]
    SEAMLESS_GREY = "#595A70"
    BACKGROUND_BUBBLES = {
        OptionType.CALL.value: "#173928",
        OptionType.PUT.value: "#3e2428" #STREAMLIT SUCCESS, ERROR BUBBLES
    }
    FONT_BUBBLES = {
        OptionType.CALL.value: "#d4f2dd",
        OptionType.PUT.value: "#f9d3d1" #STREAMLIT SUCCESS, ERROR FONTS
    }

    @classmethod
    def bubble_background_option_type(cls, option_type):
        try:
            return cls.BACKGROUND_BUBBLES[option_type]
        except:
            raise ValueError(f"Option type must be '{OptionType.CALL.value}' or '{OptionType.PUT.value}'!")
        
    @classmethod
    def bubble_font_option_type(cls, option_type):
        try:
            return cls.FONT_BUBBLES[option_type]
        except:
            raise ValueError(f"Option type must be '{OptionType.CALL.value}' or '{OptionType.PUT.value}'!") 