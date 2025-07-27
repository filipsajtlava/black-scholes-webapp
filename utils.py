import numpy as np
import streamlit as st
from inspect import signature

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

def filter_function_args(func, args_dict):
    sig = signature(func)
    return {key: value for key, value in args_dict.items() if key in sig.parameters}

