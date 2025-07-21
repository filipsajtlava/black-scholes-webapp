import streamlit as st
import pandas as pd
from black_scholes import black_scholes_price, compute_greeks
from monte_carlo import simulate_gbm_paths, monte_carlo_estimate
from black_scholes_plotting import create_basic_option_graph, create_greek_graph
from monte_carlo_plotting import plot_gbm_paths
from general import get_seed
from config import *

def uniform_columns(non_empty_column_sizes, empty_padding_size = 0.25):

    if len(non_empty_column_sizes) == 0:
        raise ValueError("Empty list of inputs")

    # Starting padding
    column_sizes = [empty_padding_size]

    for size in non_empty_column_sizes:
        column_sizes.append(size)
        column_sizes.append(empty_padding_size)

    return st.columns(column_sizes)

def get_user_inputs(key_prefix, asset_config = None, strike_config = None, 
                    time_config = None, interest_config = None, volatility_config = None,
                    paths_config = None, steps_config = None, option_type_input = None,
                    currency = CURRENCY):

    input_parameters = dict()
    
    upper_padding(75)
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

    (_, non_sliders_column, _) = uniform_columns(non_empty_column_sizes=[1.5], empty_padding_size=1)

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

        (_, option_type_column, _) = uniform_columns(non_empty_column_sizes=[2.6], empty_padding_size=1)

        with option_type_column: 

            if option_type_input:
                option_type = st.segmented_control("Option Type", ["Call", "Put"], selection_mode="single",
                                                default="Call", key=f"{key_prefix}")
                input_parameters["option_type"] = option_type

    (_, slider_left, _, slider_right, _) = st.columns([0.25, 1.5, 0.1, 1.5, 0.25])
        
    with slider_left:

        if paths_config:
            num_paths = st.number_input(label=paths_config.label, 
                                    min_value=paths_config.min, value=paths_config.default, 
                                    max_value=paths_config.max, step=paths_config.step,
                                    key=f"{key_prefix}_{paths_config.variable}", format="%2f")
            input_parameters["num_paths"] = num_paths
        
    with slider_right:

        if steps_config:
            num_steps = st.number_input(label=steps_config.label, 
                                    min_value=steps_config.min, value=steps_config.default, 
                                    max_value=steps_config.max, step=steps_config.step,
                                    key=f"{key_prefix}_{steps_config.variable}", format="%2f")
            input_parameters["num_steps"] = num_steps

    return input_parameters

def upper_padding(pixels):
    st.markdown(f"<div style='margin-top: {pixels}px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":

    st.set_page_config(page_title="Option Pricing App", layout="wide")
    tab_1, tab_2, tab_3 = st.tabs(["Math", 
                            "Option Pricing",
                            "Application of the option pricing"])

    with tab_2:
        (
            _,
            params_column,
            _,
            output_column,
            _,
        ) = uniform_columns(non_empty_column_sizes=[1, 2], empty_padding_size=0.1)

        with params_column:
            input_tab_2_1 = get_user_inputs(key_prefix="tab_2_1",
                                                asset_config=asset_price_slider,
                                                strike_config=strike_price_slider, 
                                                time_config=time_input, 
                                                interest_config=non_risk_interest_input, 
                                                volatility_config=volatility_input,
                                                option_type_input=True)

        with output_column:
            bs_tab, gmb_tab = st.tabs(["Black-Scholes Option Pricing",
                                       "Monte Carlo Option Pricing"])

            with bs_tab:

                (   _,
                    plot_column,
                    _,
                    greeks_column, 
                    _
                ) = uniform_columns([1.5, 0.5])

                with plot_column:

                    st.caption("Black-Scholes option price")
                    price_bs = black_scholes_price(**input_tab_2_1)
                    st.success(f"{input_tab_2_1["option_type"]} option price: {price_bs:.2f}{CURRENCY}")

                    graph_container_1 = st.empty()
                    
                    (_, left_toggle, right_toggle) = st.columns([0.4, 1, 1])
                    
                    with left_toggle:
                        color_toggle = st.toggle("Toggle coloring of areas", value=True)
                    with right_toggle:
                        bs_function_toggle = st.toggle("Toggle Black-Scholes price function", value=True)

                    graph_container_1.plotly_chart(create_basic_option_graph(**input_tab_2_1,
                                                        maximum_stock_value=asset_price_slider.max,
                                                        maximum_strike_value=strike_price_slider.max,
                                                        modelled_price=price_bs,
                                                        color_toggle=color_toggle,
                                                        bs_function_toggle=bs_function_toggle),
                                                use_container_width=True)

                with greeks_column:
                    upper_padding(10)
                    graph_container_2 = st.empty()

                    greeks = pd.DataFrame(compute_greeks(**input_tab_2_1), index = [0])
                    greeks.index = ["Values"]

                    upper_padding(10)

                    st.write("Greeks calculation")
                    st.table(greeks.transpose())

                    selected_greek = st.selectbox("Select Greek to plot:", greeks.columns)

                    greeks_x_options = [asset_price_slider,
                                        strike_price_slider, 
                                        time_input, 
                                        non_risk_interest_input, 
                                        volatility_input]
                    
                    selected_variable = st.selectbox("Select the x-axis variable:", greeks_x_options, format_func= lambda x: x.variable)

                    graph_container_2.plotly_chart(create_greek_graph(**input_tab_2_1, 
                                                                      x_var_config=selected_variable,
                                                                      greek_to_plot=selected_greek),
                                                   use_container_width=True, config={'displayModeBar': False})

            with gmb_tab:

                (_, plot_column, _, end_points_column, _) = uniform_columns([1.5, 0.5])

                with end_points_column:
                    upper_padding(109)
                    end_points_plot_1 = st.empty()

                    fixed_seed_toggle = st.toggle("Fixed seed", value=False)
                    if fixed_seed_toggle:
                        seed = st.number_input("Select seed",
                                               min_value=SEED_INTERVAL[0],
                                               max_value=SEED_INTERVAL[1],
                                               key="seed_toggle")
                    else:
                        seed = get_seed(SEED_INTERVAL)

                with plot_column:

                    st.caption("Monte Carlo option price")
                    price_text_container_1 = st.empty()
                    graph_container_1 = st.empty()
                    under_graph_caption_1 = st.empty()

                    (_, slider_left, _, slider_right, _) = st.columns([0.25, 1.5, 0.1, 1.5, 0.25])

                    with slider_left:
                        num_paths = st.number_input(label=paths_input.label, 
                                                    min_value=paths_input.min,
                                                    value=paths_input.default, 
                                                    max_value=paths_input.max,
                                                    step=paths_input.step,
                                                    format="%2f")

                    with slider_right:
                        num_steps = st.number_input(label=steps_input.label, 
                                                    min_value=steps_input.min,
                                                    value=steps_input.default, 
                                                    max_value=steps_input.max,
                                                    step=steps_input.step,
                                                    format="%2f")

                    input_tab_2_2 = input_tab_2_1.copy()
                    input_tab_2_2.update({"num_paths": num_paths, "num_steps": num_steps})

                    gbm_input_helper = ["S", "T", "r", "sigma", "num_paths", "num_steps"]
                    monte_carlo_input_helper = ["K", "T", "r", "option_type"]

                    gbm_input = {k: v for k, v in input_tab_2_2.items() if k in gbm_input_helper}
                    monte_carlo_input = {k: v for k, v in input_tab_2_2.items() if k in monte_carlo_input_helper}

                    geom_brown_motion_mat = simulate_gbm_paths(**gbm_input, seed=seed)

                    modelled_price_mc = monte_carlo_estimate(S_paths=geom_brown_motion_mat,
                                                            **monte_carlo_input)

                    price_text_container_1.success(
                        f"{input_tab_2_2['option_type']} option price: {modelled_price_mc}{CURRENCY}"
                    )

                    gbm_plot, end_points_plot = plot_gbm_paths(geom_brown_motion_mat,
                                                            gbm_input["T"],
                                                            gbm_input["r"],
                                                            seed)

                    graph_container_1.plotly_chart(
                        gbm_plot,
                        use_container_width=True,
                        config={"displayModeBar": False}
                    )

                    if gbm_input["num_paths"] > MAX_GBM_LINES:
                        under_graph_caption_1.caption(
                            f"Due to performance concerns this plot only shows {MAX_GBM_LINES} randomly chosen paths."
                        )

                with end_points_column:
                    end_points_plot_1.plotly_chart(end_points_plot, use_container_width=False, config={"displayModeBar": False})




    st.markdown("""
    <style>
    .block-container {
        padding-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

