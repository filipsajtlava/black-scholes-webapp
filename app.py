import streamlit as st
import pandas as pd
from pricing.black_scholes import black_scholes_price, compute_greeks
from plotting import create_basic_option_graph, create_greek_graph
from config import *

def general_padding(non_empty_column_sizes, empty_padding_size = 0.25):

    if len(non_empty_column_sizes) == 0:
        raise ValueError("Empty list of inputs")

    # Starting padding
    column_sizes = [empty_padding_size]

    for size in non_empty_column_sizes:
        column_sizes.append(size)
        column_sizes.append(empty_padding_size)

    return st.columns(column_sizes)

def get_user_inputs_bs(asset_config, strike_config, 
                       time_config, interest_config, 
                       volatility_config, key_prefix, currency = "€", strike_input = None):

    #for _ in range(3):
    #    st.write("")
            
    st.subheader("Parameters")

    S = st.slider(label=asset_config.label,
                  min_value=asset_config.min, value=asset_config.default,
                  max_value=asset_config.max,
                  step=asset_config.step, format=f"%2f {currency}",
                  key=f"{key_prefix}_{asset_config.variable}")
    
    if strike_input is not None:
        K = st.slider(label=strike_config.label,
                    min_value=strike_config.min, value=strike_config.default,
                    max_value=strike_config.max,
                    step=strike_config.step, format=f"%2f {currency}",
                    key=f"{key_prefix}_{strike_config.variable}")
    else:
        K = None

    (_, non_sliders_column, _) = general_padding(non_empty_column_sizes=[1.5], empty_padding_size=1)

    with non_sliders_column:

        T = st.number_input(label=time_config.label, 
                            min_value=time_config.min, value=time_config.default, 
                            max_value=time_config.max, step=time_config.step,
                            key=f"{key_prefix}_{time_config.variable}")
        
        r = st.number_input(label=interest_config.label, 
                            min_value=interest_config.min, value=interest_config.default, 
                            max_value= interest_config.max, step=interest_config.step,
                            key=f"{key_prefix}_{interest_config.variable}")

        sigma = st.number_input(label=volatility_config.label, 
                                min_value=volatility_config.min, max_value=volatility_config.max, 
                                value=volatility_config.default, step=volatility_config.step,
                                key=f"{key_prefix}_{volatility_config.variable}")
        
        (_, option_type_column, _) = general_padding(non_empty_column_sizes=[2.1], empty_padding_size=1)

        with option_type_column: 
            option_type = st.segmented_control("Option Type", ["Call", "Put"], selection_mode="single",
                                               default="Call", key=f"{key_prefix}")

    input_parameters = {
        "S": S,
        "K": K,
        "T": T,
        "r": r,
        "sigma": sigma,
        "option_type": option_type
    }

    return input_parameters

if __name__ == "__main__":

    st.set_page_config(page_title="Option Pricing App", layout="wide")
    tab_1, tab_2, tab_3 = st.tabs(["Mathematical Background", 
                                "Black-Scholes Option Pricing", 
                                "Monte Carlo Simulation Option Pricing"])

    with tab_1:
        st.title("The math behind the famous Black-Scholes formula")

    with tab_2:
        st.write("")
        st.write("")
        (
            _,
            params_column,
            _,
            output_column,
            _,
            greeks_column,
            _ 
        ) = general_padding(non_empty_column_sizes=[1.5, 1.5, 0.5])

        with params_column:
            input_parameters = get_user_inputs_bs(asset_price_slider,
                                                  strike_price_slider, 
                                                  time_input, 
                                                  non_risk_interest_input, 
                                                  volatility_input,
                                                  "tab_2",
                                                  strike_input=True)

        with output_column:
            st.subheader("Option Price")
            price = black_scholes_price(**input_parameters)
            st.success(f"{input_parameters["option_type"]} option price: {price:.2f}€")

            (_, output_coloring, _) = general_padding(non_empty_column_sizes=[1.25],empty_padding_size=0.75)
            
            with output_coloring:
                color_toggle = st.toggle("Toggle coloring of areas", value=True)
                bs_function_toggle = st.toggle("Toggle Black-Scholes price function", value=True)
            st.plotly_chart(create_basic_option_graph(**input_parameters,
                                                      maximum_stock_value=asset_price_slider.max,
                                                      maximum_strike_value=strike_price_slider.max,
                                                      modelled_price=price,
                                                      color_toggle=color_toggle,
                                                      bs_function_toggle=bs_function_toggle),
                            use_container_width=True)

        with greeks_column:

            graph_placeholder = st.empty()

            greeks = pd.DataFrame(compute_greeks(**input_parameters), index = [0])
            greeks.index = ["Values"]

            for _ in range(2): # Hacky way of vertical adjustment
                st.write("")

            st.write("Greeks calculation")
            st.table(greeks.transpose())

            selected_greek = st.selectbox("Select Greek to plot:", greeks.columns)

            greeks_x_options = [asset_price_slider,
                                strike_price_slider, 
                                time_input, 
                                non_risk_interest_input, 
                                volatility_input]
            
            selected_variable = st.selectbox("Select the x-axis variable:", greeks_x_options, format_func= lambda x: x.variable)

            graph_placeholder.plotly_chart(create_greek_graph(**input_parameters, 
                                                              x_var_config=selected_variable,
                                                              greek_to_plot=selected_greek),
                                           use_container_width=True, config={'displayModeBar': False})

    with tab_3:
        st.write("")
        st.write("")
        (
            _,
            params_column,
            _,
            output_column,
            _,
            greeks_column,
            _ 
        ) = general_padding(non_empty_column_sizes=[1.5, 1.5, 0.5])

        with params_column:
            input_parameters = get_user_inputs_bs(asset_price_slider,
                                                  strike_price_slider, 
                                                  time_input, 
                                                  non_risk_interest_input, 
                                                  volatility_input,
                                                  "tab_3")
            
            (_, non_sliders_column, _) = general_padding(non_empty_column_sizes=[1.5], empty_padding_size=1)

            with non_sliders_column:

                num_paths = st.number_input(label=paths_input.label, 
                                            min_value=paths_input.min, value=paths_input.default, 
                                            max_value=paths_input.max, step=paths_input.step,
                                            key=f"tab_3_{paths_input.variable}")

                num_steps = st.number_input(label=steps_input.label, 
                                            min_value=steps_input.min, value=steps_input.default, 
                                            max_value=steps_input.max, step=steps_input.step,
                                            key=f"tab_3_{steps_input.variable}")
            
    st.markdown("""
    <style>
    .block-container {
        padding-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

