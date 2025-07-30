import numpy as np
import streamlit as st
from config import StreamlitInputs
#from inspect import signature

def get_seed(seed_interval):
    rng = np.random.default_rng()
    seed = rng.integers(seed_interval[0], seed_interval[1] + 1)
    return seed

def upper_padding(pixels):
    st.markdown(f"<div style='margin-top: {pixels}px'></div>", unsafe_allow_html=True)

def remove_bottom_padding():
    st.markdown("""
    <style>
    .block-container {
        padding-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def uniform_columns(non_empty_column_sizes, empty_padding_size = 0.25):

    if len(non_empty_column_sizes) == 0:
        raise ValueError("Empty list of inputs")

    # Starting padding
    column_sizes = [empty_padding_size]

    for size in non_empty_column_sizes:
        column_sizes.append(size)
        column_sizes.append(empty_padding_size)

    return st.columns(column_sizes)

def streamlit_input_ui(variable, config, key = None, container = None):
    config_subclass = config.STREAMLIT_INPUT_CONFIGS[variable]
    key = f"{key}_{config_subclass.variable}" if key else key
    container = container if container else st 

    if config_subclass.type == StreamlitInputs.SLIDER.value:
        input_value = container.slider(label=config_subclass.label,
                                min_value=config_subclass.min,
                                value=config_subclass.default,
                                max_value=config_subclass.max,
                                step=config_subclass.step,
                                key=key
                                #format=f"%2f {config.CURRENCY}"
                                )
    elif config_subclass.type == StreamlitInputs.NUMBER_INPUT.value:
        input_value = container.number_input(label=config_subclass.label,
                                      min_value=config_subclass.min,
                                      value=config_subclass.default,
                                      max_value=config_subclass.max,
                                      step=config_subclass.step,
                                      key=key
                                      #format=f"%2f {config.CURRENCY}"
                                      )
    elif config_subclass.type == StreamlitInputs.SEGMENTED_CONTROL.value:
        input_value = container.segmented_control(label=config_subclass.label,
                                           options=config_subclass.options,
                                           default=config_subclass.default,
                                           selection_mode=config_subclass.selection_mode,
                                           key=key
        )
    else:
        raise ValueError("Undefined 'StreamlitInputs' value")
    return input_value

# Not used in the current version
#def filter_function_args(func, args_dict):
#    sig = signature(func)
#    return {key: value for key, value in args_dict.items() if key in sig.parameters}

