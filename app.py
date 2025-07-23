import streamlit as st
import pandas as pd
from black_scholes import black_scholes_price, compute_greeks
from monte_carlo import simulate_gbm_paths, monte_carlo_estimate
from black_scholes_plotting import create_basic_option_graph, create_greek_graph
from monte_carlo_plotting import plot_gbm_paths, plot_confidence_interval
from utils import get_seed
from config import AppSettings

def upper_padding(pixels):
    st.markdown(f"<div style='margin-top: {pixels}px'></div>", unsafe_allow_html=True)

def uniform_columns(non_empty_column_sizes, empty_padding_size = 0.25):

    if len(non_empty_column_sizes) == 0:
        raise ValueError("Empty list of inputs")

    # Starting padding
    column_sizes = [empty_padding_size]

    for size in non_empty_column_sizes:
        column_sizes.append(size)
        column_sizes.append(empty_padding_size)

    return st.columns(column_sizes)

def get_user_inputs(key_prefix, selected_inputs = None, config = AppSettings):

    upper_padding(75)
    st.subheader("Parameters")

    chosen_sliders = [
        config.FIX_INPUT_CONFIGS[var] for var in config.get_variables_by_type("slider")
        if var in selected_inputs
    ]
    chosen_num_inputs = [
        config.FIX_INPUT_CONFIGS[var] for var in config.get_variables_by_type("number_input")
        if var in selected_inputs
    ]
    chosen_seg_controls = [
        config.FIX_INPUT_CONFIGS[var] for var in config.get_variables_by_type("segmented_control")
        if var in selected_inputs
    ]
    
    input_parameters = dict()

    for config_class in chosen_sliders:
        input_parameters[config_class.variable] = st.slider(label=config_class.label,
                                                            min_value=config_class.min,
                                                            value=config_class.default,
                                                            max_value=config_class.max,
                                                            step=config_class.step,
                                                            key=f"{key_prefix}_{config_class.variable}",
                                                            format=f"%2f {config.CURRENCY}"
                                                            )
        
    (_, num_inputs_column, _) = uniform_columns(non_empty_column_sizes=[1.5], empty_padding_size=1)

    with num_inputs_column:

        for config_class in chosen_num_inputs:
            input_parameters[config_class.variable] = st.number_input(label=config_class.label,
                                                                      min_value=config_class.min,
                                                                      value=config_class.default,
                                                                      max_value=config_class.max,
                                                                      step=config_class.step,
                                                                      key=f"{key_prefix}_{config_class.variable}"
                                                                      )

        (_, option_type_column, _) = uniform_columns(non_empty_column_sizes=[2.6], empty_padding_size=1)

        with option_type_column: 

            for config_class in chosen_seg_controls:
                input_parameters[config_class.variable] = st.segmented_control(label=config_class.label,
                                                                               options=config_class.options,
                                                                               default=config_class.default,
                                                                               selection_mode=config_class.selection_mode,
                                                                               key=f"{key_prefix}_{config_class.variable}"
                                                                               )

    return input_parameters

def stage_bs_subtab(input_parameters, config = AppSettings):

    (   _,
        plot_column,
        _,
        greeks_column, 
        _
    ) = uniform_columns([1.5, 0.5])

    with plot_column:

        price_bs = black_scholes_price(**input_parameters)

        st.caption("Black-Scholes option price")
        st.success(f"{input_parameters["option_type"]} option price: {price_bs:.2f}{config.CURRENCY}")
        main_bs_plot_container = st.empty()
        
        (_, left_toggle, right_toggle) = st.columns([0.4, 1, 1])
                    
        with left_toggle:
            color_toggle = st.toggle("Toggle coloring of areas", value=True)
        with right_toggle:
            bs_function_toggle = st.toggle("Toggle Black-Scholes price function", value=True)

        main_bs_plot = create_basic_option_graph(**input_parameters,
                                                 maximum_stock_value=config.FIX_INPUT_CONFIGS["S"].max,
                                                 maximum_strike_value=config.FIX_INPUT_CONFIGS["K"].max,
                                                 modelled_price=price_bs,
                                                 color_toggle=color_toggle,
                                                 bs_function_toggle=bs_function_toggle
                                                 )
                    
        main_bs_plot_container.plotly_chart(main_bs_plot, use_container_width=True)

    with greeks_column:

        upper_padding(10)
        mini_greeks_plot_container = st.empty()

        greeks = pd.DataFrame(compute_greeks(**input_parameters), index = [0])
        greeks.index = ["Values"]

        upper_padding(10)
        st.write("Greeks calculation")
        st.table(greeks.transpose())

        selected_greek = st.selectbox("Select Greek to plot:", greeks.columns)
        greeks_x_options = config.get_variables_by_type("slider") + config.get_variables_by_type("number_input")
        selected_variable = st.selectbox("Select the x-axis variable:", greeks_x_options)

        mini_greeks_plot = create_greek_graph(**input_parameters,
                                              x_var_config=config.FIX_INPUT_CONFIGS[selected_variable],
                                              greek_to_plot=selected_greek
                                              )
        
        mini_greeks_plot_container.plotly_chart(mini_greeks_plot, use_container_width=True, config={'displayModeBar': False})

def stage_gmb_subtab(input_parameters, config = AppSettings):
    
    (
        _,
        plot_column, 
        _, 
        end_points_column, 
        _
    ) = uniform_columns([1.5, 0.5])

    with end_points_column:
        upper_padding(1)
        confidence_interval_container = st.empty()
        end_points_container = st.empty()

        fixed_seed_toggle = st.toggle("Fixed seed", value=False)
        if fixed_seed_toggle:
            seed = st.number_input("Select seed",
                                   min_value=config.SEED_INTERVAL[0],
                                   max_value=config.SEED_INTERVAL[1],
                                   key="seed_toggle"
                                   )
        else:
            seed = get_seed(config.SEED_INTERVAL)

    with plot_column:

        st.caption("Monte Carlo option price")
        modelled_price_container = st.empty()
        main_gbm_plot_container = st.empty()
        under_plot_caption_container = st.empty()

        (_, input_left, _, input_right, _) = st.columns([0.25, 1.5, 0.1, 1.5, 0.25])

        with input_left:
            num_paths = st.number_input(label=config.MC_INPUT_CONFIGS["paths"].label, 
                                        min_value=config.MC_INPUT_CONFIGS["paths"].min,
                                        value=config.MC_INPUT_CONFIGS["paths"].default, 
                                        max_value=config.MC_INPUT_CONFIGS["paths"].max,
                                        step=config.MC_INPUT_CONFIGS["paths"].step,
                                        format="%2f"
                                        )

        with input_right:
            num_steps = st.number_input(label=config.MC_INPUT_CONFIGS["steps"].label, 
                                        min_value=config.MC_INPUT_CONFIGS["steps"].min,
                                        value=config.MC_INPUT_CONFIGS["steps"].default, 
                                        max_value=config.MC_INPUT_CONFIGS["steps"].max,
                                        step=config.MC_INPUT_CONFIGS["steps"].step,
                                        format="%2f"
                                        )

        input_parameters = input_parameters.copy()
        input_parameters.update({"num_paths": num_paths, "num_steps": num_steps})

        gbm_input_helper = ["S", "T", "r", "sigma", "num_paths", "num_steps"]
        monte_carlo_input_helper = ["K", "T", "r", "option_type"]

        gbm_input = {k: v for k, v in input_parameters.items() if k in gbm_input_helper}
        monte_carlo_input = {k: v for k, v in input_parameters.items() if k in monte_carlo_input_helper}

        geom_brown_motion_mat = simulate_gbm_paths(**gbm_input, seed=seed)
        modelled_price_mc, confidence_interval = monte_carlo_estimate(S_paths=geom_brown_motion_mat, **monte_carlo_input)

        modelled_price_container.success(
            f"{input_parameters['option_type']} option price: {modelled_price_mc:.2f}{config.CURRENCY}"
        )

        if modelled_price_mc > 0:
            CI_plot = plot_confidence_interval(modelled_price_mc, confidence_interval, monte_carlo_input["option_type"])
            confidence_interval_container.plotly_chart(CI_plot, 
                                                       use_container_width=True,
                                                       config={"displayModeBar": False})
        else:
            confidence_interval_container.markdown(
                """
                <div style="height: 90px; visibility: hidden;">&nbsp;</div>
                """,
                unsafe_allow_html=True
            )

        gbm_plot, end_points_plot = plot_gbm_paths(S_paths=geom_brown_motion_mat,
                                                   T=gbm_input["T"],
                                                   r=gbm_input["r"],
                                                   seed=seed,
                                                   config=AppSettings
                                                   )

        main_gbm_plot_container.plotly_chart(
            gbm_plot,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        if gbm_input["num_paths"] > config.MAX_GBM_LINES:
            under_plot_caption_container.caption(
                f"Due to performance concerns this plot only shows {config.MAX_GBM_LINES} randomly chosen paths."
            )

    with end_points_column:
        end_points_container.plotly_chart(end_points_plot, use_container_width=False, config={"displayModeBar": False})

if __name__ == "__main__":

    st.set_page_config(page_title="Option Pricing App", layout="wide")
    tab_1, tab_2, tab_3 = st.tabs(["Math", 
                                   "Option Pricing",
                                   "Application of the option pricing"])

    with tab_2:
        (
            _,
            parameter_input_column,
            _,
            output_column,
            _,
        ) = uniform_columns(non_empty_column_sizes=[1, 2], empty_padding_size=0.1)

        with parameter_input_column:
            fixed_inputs = get_user_inputs(key_prefix="tab_2_1", selected_inputs=["S", "K", "T", "r", "sigma", "option_type"])

        with output_column:
            bs_tab, gmb_tab = st.tabs(["Black-Scholes Option Pricing",
                                       "Monte Carlo Option Pricing"])

            with bs_tab:
                stage_bs_subtab(fixed_inputs)

            with gmb_tab:
                stage_gmb_subtab(fixed_inputs)




    st.markdown("""
    <style>
    .block-container {
        padding-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

