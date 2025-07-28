import streamlit as st
import pandas as pd
from st_flexible_callout_elements import flexible_callout
from black_scholes import black_scholes_price, compute_greeks
from monte_carlo import simulate_gbm_paths, monte_carlo_estimate
from black_scholes_plotting import plot_payoffs, create_greek_graph
from monte_carlo_plotting import plot_gbm_paths, plot_confidence_interval
from utils import get_seed, upper_padding, remove_bottom_padding, uniform_columns, filter_function_args
from config import AppSettings, Colors, Greeks, VariableKey
from candlestick_plotting import plot_candlestick_asset

def get_user_inputs(key_prefix, config, selected_inputs = None):

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

        (_, option_type_column, _) = uniform_columns(non_empty_column_sizes=[2.65], empty_padding_size=1)

        with option_type_column: 

            for config_class in chosen_seg_controls:
                input_parameters[config_class.variable] = st.segmented_control(label=config_class.label,
                                                                               options=config_class.options,
                                                                               default=config_class.default,
                                                                               selection_mode=config_class.selection_mode,
                                                                               key=f"{key_prefix}_{config_class.variable}"
                                                                               )

    return input_parameters

def render_output_price_bubble(option_type, modelled_price, config, color_config, font_size = 20, padding = 10):
    flexible_callout(f"{option_type} option price: {modelled_price:.2f}{config.CURRENCY}",
                     background_color=color_config.bubble_background_option_type(option_type),
                     font_color=color_config.bubble_font_option_type(option_type),
                     font_size=font_size,
                     alignment="center",
                     padding=padding
                     )

def create_greek_table(inputs):
    greeks = pd.DataFrame(compute_greeks(**inputs), index = [0])
    greeks.index = ["Values"]
    st.table(greeks.transpose())
    return greeks
    
def render_bs_graph_toggles(config):
    selected_greek = st.selectbox("Select Greek to plot:", [g.value for g in Greeks])
    greeks_x_options = config.get_variables_by_type("slider") + config.get_variables_by_type("number_input")
    selected_variable = st.selectbox("Select the x-axis variable:", greeks_x_options)

    return selected_greek, selected_variable

def stage_bs_subtab(input_parameters, config, color_config):

    (   _,
        plot_column,
        _,
        greeks_column, 
        _
    ) = uniform_columns([1.5, 0.5])

    with plot_column:

        price_bs = black_scholes_price(**input_parameters)
        st.caption("Black-Scholes option price")
        render_output_price_bubble(option_type=input_parameters[VariableKey.OPTION_TYPE.value], 
                                   modelled_price=price_bs,
                                   config=config,
                                   color_config=color_config
                                   )

        main_bs_plot_container = st.empty()
        
        (_, left_toggle, right_toggle) = st.columns([0.4, 1, 1])
                    
        with left_toggle:
            color_toggle = st.toggle("Toggle coloring of areas", value=True)
        with right_toggle:
            bs_function_toggle = st.toggle("Toggle Black-Scholes price function", value=True)

        main_bs_plot = plot_payoffs(**input_parameters,
                                    maximum_stock_value=config.FIX_INPUT_CONFIGS[VariableKey.S.value].max,
                                    maximum_strike_value=config.FIX_INPUT_CONFIGS[VariableKey.K.value].max,
                                    modelled_price=price_bs,
                                    color_config=color_config,
                                    color_toggle=color_toggle,
                                    bs_function_toggle=bs_function_toggle
                                    )
                    
        main_bs_plot_container.plotly_chart(main_bs_plot, use_container_width=True)

    with greeks_column:

        upper_padding(10)
        mini_greeks_plot_container = st.empty()
        upper_padding(10)
        st.write("Greeks calculation")

        create_greek_table(input_parameters)
        selected_greek, selected_variable = render_bs_graph_toggles(config = config)

        mini_greeks_plot = create_greek_graph(input_parameters=input_parameters,
                                              x_var_config=config.FIX_INPUT_CONFIGS[selected_variable],
                                              greek_to_plot=selected_greek,
                                              color_config=color_config
                                              )
        
        mini_greeks_plot_container.plotly_chart(mini_greeks_plot, use_container_width=True, config={'displayModeBar': False})



def render_input_seed(config):
    fixed_seed_toggle = st.toggle("Fixed seed", value=False)
    if fixed_seed_toggle:
        seed = st.number_input("Select seed",
                                min_value=config.SEED_INTERVAL[0],
                                max_value=config.SEED_INTERVAL[1],
                                key="seed_toggle"
                                )
    else:
        seed = get_seed(config.SEED_INTERVAL)
    return seed

def render_ci_plot(modelled_price_mc, confidence_interval, option_type, container):
    if modelled_price_mc > 0:
        CI_plot = plot_confidence_interval(modelled_price_mc, confidence_interval, option_type)
        container.plotly_chart(CI_plot, 
                               use_container_width=True,
                               config={"displayModeBar": False}
                               )
    else:
        container.markdown(
            """
            <div style="height: 90px; visibility: hidden;">&nbsp;</div>
            """,
            unsafe_allow_html=True
        )

def render_mc_input(variable_input, config):
    input = st.number_input(label=config.MC_INPUT_CONFIGS[variable_input].label, 
                            min_value=config.MC_INPUT_CONFIGS[variable_input].min,
                            value=config.MC_INPUT_CONFIGS[variable_input].default, 
                            max_value=config.MC_INPUT_CONFIGS[variable_input].max,
                            step=config.MC_INPUT_CONFIGS[variable_input].step,
                            format="%2f"
                            )
    return input

def stage_mc_subtab(input_parameters, config, color_config):
    
    (
        _,
        plot_column, 
        _, 
        seed_endpoints_column, 
        _
    ) = uniform_columns([1.5, 0.5])

    with seed_endpoints_column:
        upper_padding(1)
        confidence_interval_container = st.empty()
        end_points_container = st.empty()
        seed = render_input_seed(config)

    with plot_column:
        st.caption("Monte Carlo option price")
        modelled_price_container = st.empty()
        main_gbm_plot_container = st.empty()
        under_plot_caption_container = st.empty()

        (_, input_left, _, input_right, _) = st.columns([0.25, 1.5, 0.1, 1.5, 0.25])
        with input_left:
            num_paths = render_mc_input(variable_input=VariableKey.PATHS.value, config=config)
        with input_right:
            num_steps = render_mc_input(variable_input=VariableKey.STEPS.value, config=config)

        input_parameters = input_parameters.copy()
        input_parameters.update({VariableKey.PATHS.value: num_paths, VariableKey.STEPS.value: num_steps})

        gbm_args = filter_function_args(simulate_gbm_paths, input_parameters)
        geom_brown_motion_mat = simulate_gbm_paths(**gbm_args, seed=seed)
        mc_args = filter_function_args(monte_carlo_estimate, input_parameters)
        modelled_price_mc, confidence_interval = monte_carlo_estimate(S_paths=geom_brown_motion_mat, **mc_args)

        with modelled_price_container:
            render_output_price_bubble(option_type=input_parameters["option_type"], 
                                       modelled_price=modelled_price_mc,
                                       config=config,
                                       color_config=color_config
                                       )

        gbm_plot, end_points_plot = plot_gbm_paths(S_paths=geom_brown_motion_mat,
                                                   T=input_parameters["T"],
                                                   r=input_parameters["r"],
                                                   seed=seed,
                                                   config=config
                                                   )

        main_gbm_plot_container.plotly_chart(
            gbm_plot,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        if input_parameters["num_paths"] > config.MAX_GBM_LINES:
            under_plot_caption_container.caption(
                f"Due to performance concerns this plot only shows {config.MAX_GBM_LINES} randomly chosen paths."
            )

    with seed_endpoints_column:
        render_ci_plot(modelled_price_mc=modelled_price_mc,
                       confidence_interval=confidence_interval,
                       option_type=input_parameters["option_type"],
                       container=confidence_interval_container
                       )

        end_points_container.plotly_chart(end_points_plot,
                                          use_container_width=False, 
                                          config={"displayModeBar": False}
                                          )



def stage_candlestick_tab(key_prefix, config, color_config):
    (
        _,
        main_plot_column,
        _
    ) = uniform_columns(non_empty_column_sizes=[1], empty_padding_size=1)

    with main_plot_column:
        
        selected_ticker = st.multiselect("Select asset to plot:",
                                         ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "NVDA"],
                                         max_selections=1)

        main_plot_container = st.empty()

        (
            _,
            interval_input_column,
            _,
            stats_column,
            _
        ) = uniform_columns(non_empty_column_sizes=[2,2])

        with interval_input_column:
            segmented_control_interval_container = st.empty()
        
        with stats_column:
            stats_container = st.empty()

        selected_interval = segmented_control_interval_container.segmented_control(
            label=config.CANDLESTICK_CONFIGS["interval"].label,
            options=config.CANDLESTICK_CONFIGS["interval"].options,
            default=config.CANDLESTICK_CONFIGS["interval"].default,
            selection_mode=config.CANDLESTICK_CONFIGS["interval"].selection_mode,
            key=f"{key_prefix}_{config.CANDLESTICK_CONFIGS["interval"].variable}"
        )

        plot_candlestick_asset(selected_ticker=selected_ticker,
                               selected_interval=)


if __name__ == "__main__":

    st.set_page_config(page_title="Option Pricing App", layout="wide")
    tab_1, tab_2, tab_3 = st.tabs(["Math", 
                                   "Option Pricing",
                                   "Application of the option pricing"])

    with tab_1:
        pass

    with tab_2:
        (
            _,
            parameter_input_column,
            _,
            output_column,
            _,
        ) = uniform_columns(non_empty_column_sizes=[1, 2], empty_padding_size=0.1)

        with parameter_input_column:
            fixed_inputs = get_user_inputs(key_prefix="tab_2_1",
                                           config= AppSettings,
                                           selected_inputs=["S", "K", "T", "r", "sigma", "option_type"]
                                           )

        with output_column:
            bs_tab, mc_tab = st.tabs(["Black-Scholes Option Pricing",
                                       "Monte Carlo Option Pricing"]
                                       )

            with bs_tab:
                stage_bs_subtab(fixed_inputs, 
                                config=AppSettings, 
                                color_config=Colors
                                )

            with mc_tab:
                stage_mc_subtab(fixed_inputs, 
                                config=AppSettings, 
                                color_config=Colors
                                 )
                
    with tab_3:
        stage_candlestick_tab(key_prefix="tab_3_1",
                              config=AppSettings,
                              color_config=Colors
                              )



    remove_bottom_padding()

