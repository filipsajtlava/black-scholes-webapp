import streamlit as st
import pandas as pd
from black_scholes import black_scholes_price, compute_greeks
from monte_carlo import simulate_gbm_paths
from black_scholes_plotting import create_basic_option_graph, create_greek_graph
from monte_carlo_plotting import plot_gbm_paths
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

def get_user_inputs_bs(key_prefix, asset_config = None, strike_config = None, 
                       time_config = None, interest_config = None, volatility_config = None,
                       paths_config = None, steps_config = None, option_type_input = None,
                       currency = "€"):

    input_parameters = dict()

    #for _ in range(3):
    #    st.write("")
            
    st.subheader("Parameters")

    if asset_config:
        S = st.slider(label=asset_config.label,
                    min_value=asset_config.min, value=asset_config.default,
                    max_value=asset_config.max,
                    step=asset_config.step, format=f"%2f {currency}",
                    key=f"{key_prefix}_{asset_config.variable}")
        input_parameters["S"] = S
    
    if strike_config:
        K = st.slider(label=strike_config.label,
                    min_value=strike_config.min, value=strike_config.default,
                    max_value=strike_config.max,
                    step=strike_config.step, format=f"%2f {currency}",
                    key=f"{key_prefix}_{strike_config.variable}")
        input_parameters["K"] = K

    (_, non_sliders_column, _) = general_padding(non_empty_column_sizes=[1.5], empty_padding_size=1)

    with non_sliders_column:

        if time_config:
            T = st.number_input(label=time_config.label, 
                                min_value=time_config.min, value=time_config.default, 
                                max_value=time_config.max, step=time_config.step,
                                key=f"{key_prefix}_{time_config.variable}")
            input_parameters["T"] = T
        
        if interest_config:
            r = st.number_input(label=interest_config.label, 
                                min_value=interest_config.min, value=interest_config.default, 
                                max_value= interest_config.max, step=interest_config.step,
                                key=f"{key_prefix}_{interest_config.variable}")
            input_parameters["r"] = r

        if volatility_config:
            sigma = st.number_input(label=volatility_config.label, 
                                    min_value=volatility_config.min, max_value=volatility_config.max, 
                                    value=volatility_config.default, step=volatility_config.step,
                                    key=f"{key_prefix}_{volatility_config.variable}")
            input_parameters["sigma"] = sigma

        if paths_config:
            num_paths = st.number_input(label=paths_config.label, 
                                        min_value=paths_config.min, value=paths_config.default, 
                                        max_value=paths_config.max, step=paths_config.step,
                                        key=f"{key_prefix}_{paths_config.variable}", format="%2f")
            input_parameters["num_paths"] = num_paths
        
        if steps_config:
            num_steps = st.number_input(label=steps_config.label, 
                                        min_value=steps_config.min, value=steps_config.default, 
                                        max_value=steps_config.max, step=steps_config.step,
                                        key=f"{key_prefix}_{steps_config.variable}", format="%2f")
            input_parameters["num_steps"] = num_steps

        (_, option_type_column, _) = general_padding(non_empty_column_sizes=[2.1], empty_padding_size=1)

        with option_type_column: 

            if option_type_input:
                option_type = st.segmented_control("Option Type", ["Call", "Put"], selection_mode="single",
                                               default="Call", key=f"{key_prefix}")
                input_parameters["option_type"] = option_type

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
            input_tab_2 = get_user_inputs_bs(key_prefix="tab_2",
                                             asset_config=asset_price_slider,
                                             strike_config=strike_price_slider, 
                                             time_config=time_input, 
                                             interest_config=non_risk_interest_input, 
                                             volatility_config=volatility_input,
                                             option_type_input=True)

        with output_column:
            st.subheader("Option Price")
            price = black_scholes_price(**input_tab_2)
            st.success(f"{input_tab_2["option_type"]} option price: {price:.2f}€")

            (_, output_coloring, _) = general_padding(non_empty_column_sizes=[1.25],empty_padding_size=0.75)
            
            with output_coloring:
                color_toggle = st.toggle("Toggle coloring of areas", value=True)
                bs_function_toggle = st.toggle("Toggle Black-Scholes price function", value=True)
            st.plotly_chart(create_basic_option_graph(**input_tab_2,
                                                      maximum_stock_value=asset_price_slider.max,
                                                      maximum_strike_value=strike_price_slider.max,
                                                      modelled_price=price,
                                                      color_toggle=color_toggle,
                                                      bs_function_toggle=bs_function_toggle),
                            use_container_width=True)

        with greeks_column:

            graph_placeholder = st.empty()

            greeks = pd.DataFrame(compute_greeks(**input_tab_2), index = [0])
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

            graph_placeholder.plotly_chart(create_greek_graph(**input_tab_2, 
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
            placeholder,
            _ 
        ) = general_padding(non_empty_column_sizes=[1.5, 1.5, 0.5])

        with params_column:
            input_tab_3 = get_user_inputs_bs(key_prefix="tab_3",
                                             asset_config=asset_price_slider,
                                             time_config=time_input, 
                                             interest_config=non_risk_interest_input, 
                                             volatility_config=volatility_input,
                                             paths_config=paths_input,
                                             steps_config=steps_input,
                                             option_type_input=False)
                
        with output_column:
            st.subheader("Simulation")

            geom_brown_motion_y = simulate_gbm_paths(**input_tab_3)
            st.plotly_chart(plot_gbm_paths(geom_brown_motion_y  , input_tab_3["T"]),
                            use_container_width=True)
            if input_tab_3["num_paths"] > MAX_GBM_LINES:
                st.caption(f"Due to performance concerns this plot only shows {MAX_GBM_LINES} randomly chosen paths.")
            
    st.markdown("""
    <style>
    .block-container {
        padding-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

