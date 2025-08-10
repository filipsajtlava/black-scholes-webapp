import streamlit as st
import pandas as pd
from st_flexible_callout_elements import flexible_callout
from black_scholes import black_scholes_price, compute_greeks
from monte_carlo import simulate_gbm_paths, monte_carlo_estimate
from stocks_options import get_possible_sp500_tickers, get_stock_data, get_options_data
from black_scholes_plotting import plot_payoffs, create_greek_graph
from monte_carlo_plotting import plot_gbm_paths, plot_confidence_interval
from utils import *
from config import AppSettings, Colors, Greeks, VariableKey, StreamlitInputs, OptionType
from candlestick_plotting import plot_candlestick_asset

def get_user_inputs(key_prefix, config, selected_inputs = None):

    upper_padding(75)
    st.subheader("Parameters")

    slider_vars = [
        var for var in config.get_variables_by_type(StreamlitInputs.SLIDER.value)
        if var in selected_inputs
    ]
    number_input_vars = [
        var for var in config.get_variables_by_type(StreamlitInputs.NUMBER_INPUT.value)
        if var in selected_inputs
    ]
    segmented_control_vars = [
        var for var in config.get_variables_by_type(StreamlitInputs.SEGMENTED_CONTROL.value)
        if var in selected_inputs
    ]
    
    input_parameters = dict()

    for var in slider_vars:
        input_parameters[var] = streamlit_input_ui(variable=var, key=key_prefix, config=config)
        
    (_, num_inputs_column, _) = uniform_columns(non_empty_column_sizes=[1.5], empty_padding_size=1)

    with num_inputs_column:
        for var in number_input_vars:
            input_parameters[var] = streamlit_input_ui(variable=var, key=key_prefix, config=config)

        (_, option_type_column, _) = uniform_columns(non_empty_column_sizes=[2.65], empty_padding_size=1)

        with option_type_column: 
            for var in segmented_control_vars:
                input_parameters[var] = streamlit_input_ui(variable=var, key=key_prefix, config=config)

    return input_parameters

def render_output_price_bubble(option_type, modelled_price, config, color_config, font_size = 20, padding = 10):
    flexible_callout(f"{option_type} option price: {modelled_price:.2f} {config.CURRENCY}",
                     background_color=color_config.bubble_background_option_type(option_type),
                     font_color=color_config.bubble_font_option_type(option_type),
                     font_size=font_size,
                     alignment="center",
                     padding=padding
                     )

def create_greek_table(inputs):
    greeks = pd.DataFrame(compute_greeks(inputs), index = [0])
    greeks.index = ["Values"]
    st.table(greeks.transpose())
    return greeks
    
def render_bs_greek_inputs(input_parameters, config):
    selected_greek = st.selectbox("Select Greek to plot:", [g.value for g in Greeks])
    greeks_x_options = [config.STREAMLIT_INPUT_CONFIGS[key].variable 
                        for key in input_parameters.keys()]
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

        price_bs = black_scholes_price(input_parameters)
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

        main_bs_plot = plot_payoffs(input_parameters,
                                    modelled_price=price_bs,
                                    config=config,
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
        selected_greek, selected_variable = render_bs_greek_inputs(input_parameters, config=config)

        mini_greeks_plot = create_greek_graph(selected_parameters=input_parameters,
                                              x_var_config=config.STREAMLIT_INPUT_CONFIGS[selected_variable],
                                              greek_to_plot=selected_greek,
                                              color_config=color_config
                                              )
        
        mini_greeks_plot_container.plotly_chart(mini_greeks_plot, use_container_width=True, config={'displayModeBar': False})



def cache_mc_results(input_parameters, config, color_config):
    # Modelling
    geom_brown_motion_mat = simulate_gbm_paths(selected_parameters=input_parameters)
    modelled_price_mc, confidence_interval = monte_carlo_estimate(S_paths=geom_brown_motion_mat,
                                                                  selected_parameters=input_parameters
                                                                  )
    gbm_plot, end_points_plot = plot_gbm_paths(S_paths=geom_brown_motion_mat,
                                               T=input_parameters[VariableKey.T.value],
                                               r=input_parameters[VariableKey.R.value],
                                               seed=input_parameters["seed"],
                                               config=config,
                                               color_config=color_config
                                               )

    st.session_state["modelling_result"] = {
        "modelled_price": modelled_price_mc,
        "confidence_interval": confidence_interval,
        "gbm_plot": gbm_plot,
        "end_points_plot": end_points_plot
    }

def refresh_mc_if_inputs_changed(input_parameters, fixed_seed_toggle, position_column, config, color_config):

    # initialize for the first time
    if "last_inputs" not in st.session_state:
        st.session_state["last_inputs"] = {}
    if "last_seed" not in st.session_state:
        st.session_state["last_seed"] = None

    # if the last inputs aren't the same as the new ones, we will have to remodel the plot
    
    # important to note, that if the last inputs didn't get changed, we don't want to generate a new seed
    # so if the seed is toggled off (random seed), we don't want to actually get it

    # on the other hand, if it's toggled on, nothing changes anyways

    if fixed_seed_toggle:
        with position_column:
            st.session_state["seed"] = st.number_input("Select seed",
                                                       min_value=config.SEED_INTERVAL[0],
                                                       max_value=config.SEED_INTERVAL[1]
                                                       )
    else: # seed is random
        if st.session_state["last_inputs"] != input_parameters:
            st.session_state["seed"] = get_seed(seed_interval=config.SEED_INTERVAL)
    seed = st.session_state["seed"]
    
    if st.session_state["last_inputs"] != input_parameters or st.session_state["last_seed"] != seed:
        input_parameters["seed"] = seed
        cache_mc_results(input_parameters=input_parameters, config=config, color_config=color_config)
    else:
        input_parameters["seed"] = seed

    st.session_state["last_seed"] = input_parameters.pop("seed")
    st.session_state["last_inputs"] = input_parameters

def render_ci_plot(modelled_price_mc, confidence_interval, option_type, container, color_config):
    if modelled_price_mc > 0:
        CI_plot = plot_confidence_interval(modelled_price_mc, confidence_interval, option_type, color_config)
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

def render_mc_input(config):
    (_, input_left, _, input_right, _) = st.columns([0.25, 1.5, 0.1, 1.5, 0.25])
    with input_left:
        num_paths = streamlit_input_ui(variable=VariableKey.PATHS.value, config=config)
    with input_right:
        num_steps = streamlit_input_ui(variable=VariableKey.STEPS.value, config=config)
    
    return num_paths, num_steps

def stage_mc_subtab(input_parameters, config, color_config):
    (
        _,
        plot_column, 
        _, 
        seed_endpoints_column, 
        _
    ) = uniform_columns([1.5, 0.5])

    mc_parameters = input_parameters.copy()

    # get the mc-specific inputs along with initializing containers for the plot and output
    with plot_column:
        st.caption("Monte Carlo option price")

        modelled_price_container = st.empty()
        main_gbm_plot_container = st.empty()
        under_plot_caption_container = st.empty()

        num_paths, num_steps = render_mc_input(config=config)
        mc_parameters.update({
            VariableKey.PATHS.value: num_paths,
            VariableKey.STEPS.value: num_steps, 
        })

    # initialize the last column where ci-interval, endpoints and seed toggle lies
    with seed_endpoints_column:
        upper_padding(1)
        confidence_interval_container = st.empty()
        end_points_container = st.empty()
        fixed_seed_toggle = st.toggle("Fixed seed", value=False)

    refresh_mc_if_inputs_changed(input_parameters=mc_parameters,
                                 fixed_seed_toggle=fixed_seed_toggle,
                                 position_column=seed_endpoints_column,
                                 config=config,
                                 color_config=color_config
                                 )

    modelling_result = st.session_state["modelling_result"]
    modelled_price_mc = modelling_result["modelled_price"]
    confidence_interval = modelling_result["confidence_interval"]
    gbm_plot = modelling_result["gbm_plot"]
    end_points_plot = modelling_result["end_points_plot"]

    with modelled_price_container:
        render_output_price_bubble(option_type=mc_parameters[VariableKey.OPTION_TYPE.value], 
                                    modelled_price=modelled_price_mc,
                                    config=config,
                                    color_config=color_config
                                    )

        main_gbm_plot_container.plotly_chart(
            gbm_plot,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        if mc_parameters[VariableKey.PATHS.value] > config.MAX_GBM_LINES:
            under_plot_caption_container.caption(
                f"Due to performance concerns this plot only shows {config.MAX_GBM_LINES} randomly chosen paths."
            )

    with seed_endpoints_column:
        render_ci_plot(modelled_price_mc=modelled_price_mc,
                       confidence_interval=confidence_interval,
                       option_type=mc_parameters[VariableKey.OPTION_TYPE.value],
                       container=confidence_interval_container,
                       color_config=color_config
                       )

        end_points_container.plotly_chart(end_points_plot,
                                          use_container_width=False, 
                                          config={"displayModeBar": False}
                                          )



def render_change_bubble(df, container, color_config, font_size = 20, padding = 10):
    try:
        start_price = df.iloc[0]["Close"]
        end_price = df.iloc[-1]["Close"]
        relative_change = (end_price - start_price) / start_price
    except:
        raise ValueError("Please check your network connection")

    if relative_change > 0:
        option_type = OptionType.CALL.value
        arrow = "▲"
    else:
        option_type = OptionType.PUT.value
        arrow = "▼"

    relative_change = round(abs(relative_change) * 100, 2)

    flexible_callout(f"{arrow} {relative_change}%*",
                     background_color=color_config.bubble_background_option_type(option_type),
                     font_color=color_config.bubble_font_option_type(option_type),
                     font_size=font_size,
                     alignment="center",
                     padding=padding,
                     container=container
                     )

def render_candlestick_plot(key_prefix, config, color_config):
    upper_padding(10)
    (
        _,
        multiselect_column,
        _,
        change_column,
        _
    ) = uniform_columns(non_empty_column_sizes=[2,1.5], empty_padding_size=0.5)

    with multiselect_column:
        selected_ticker = st.multiselect("Select asset to plot:", get_possible_sp500_tickers(), max_selections=1)
        if selected_ticker:
            selected_ticker = selected_ticker[0]
    with change_column:
        upper_padding(22)
        change_bubble_container = st.empty()

    main_plot_container = st.empty()
    (
        _,
        interval_input_column,
        _
    ) = uniform_columns(non_empty_column_sizes=[1.7], empty_padding_size=1)

    with interval_input_column:
        segmented_control_interval_container = st.empty()

    if selected_ticker:
        selected_interval = streamlit_input_ui(variable=VariableKey.INTERVAL.value, 
                                               config=config,
                                               key=key_prefix,
                                               container=segmented_control_interval_container
                                               )
        if selected_interval is None:
            raise ValueError("Please select a valid time interval option")
        
        stock_data = get_stock_data(selected_ticker=selected_ticker, selected_interval=selected_interval, config=config)

        candlestick_plot = plot_candlestick_asset(df=stock_data,
                                                    selected_interval=selected_interval,
                                                    color_config=color_config
                                                    )
        main_plot_container.plotly_chart(candlestick_plot)
        render_change_bubble(df=stock_data, container=change_bubble_container, color_config=color_config)
        st.caption(f"*Relative price change in the last {interval_to_text(selected_interval, config)}")
        end_price = stock_data.iloc[-1]["Close"]

    return selected_ticker, end_price if selected_ticker else None

def render_option_selection_input(df):
    selection = df.index
    selected_option = st.selectbox("Select an option:", selection)
    return selected_option

def render_price_bubble(df, index, option_type, config, color_config, font_size = 20, padding = 10):
    upper_padding(5)
    price = (df.loc[index, "Bid"] + df.loc[index, "Ask"]) / 2
    flexible_callout(f"{price:.2f} {config.CURRENCY}",
                     background_color=color_config.bubble_background_option_type(option_type),
                     font_color=color_config.bubble_font_option_type(option_type),
                     font_size=font_size,
                     alignment="center",
                     padding=padding
                     )

def stage_option_pricing(key_prefix, selected_ticker, strike_price, config, color_config):
    if selected_ticker:
        upper_padding(10)
        title_container = st.empty()
        table_container = st.empty()

        (
            _,
            option_type_selection_column,
            _,
            option_selection_column,
            _,
            option_price_column,
            _,
        ) = uniform_columns(non_empty_column_sizes=[1, 1.5, 1], empty_padding_size=0.5)

        with option_type_selection_column:
            option_type = streamlit_input_ui(variable=VariableKey.OPTION_TYPE.value,
                                             config=config,
                                             key=key_prefix
                                             )

        options_data, closest_expiry = get_options_data(selected_ticker=selected_ticker, 
                                        option_type=option_type, 
                                        strike_price=strike_price, 
                                        config=config
                                        )
        
        with option_selection_column:
            selected_option = render_option_selection_input(df=options_data)

        with option_price_column:
            render_price_bubble(df=options_data, 
                                index=selected_option, 
                                option_type=option_type,
                                config=config, 
                                color_config=color_config)


        title_container.write(f"Option market prices (with expiry at {closest_expiry})")
        options_data = options_data.style.apply(highlight_chosen_row, 
                                                target_index=[selected_option], 
                                                option_type=option_type, 
                                                axis=None
                                                )
        table_container.dataframe(options_data)
    

if __name__ == "__main__":

    st.set_page_config(page_title="Option Pricing App", layout="wide")
    tab_1, tab_2, tab_3 = st.tabs(["Math", "Option Pricing", "Option Pricing in Practice"])

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

        main_inputs = [VariableKey.S.value,
                       VariableKey.K.value,
                       VariableKey.T.value,
                       VariableKey.R.value,
                       VariableKey.SIGMA.value,
                       VariableKey.OPTION_TYPE.value
                       ]
        with parameter_input_column:
            fixed_inputs = get_user_inputs(key_prefix="tab_2_1",
                                           config=AppSettings,
                                           selected_inputs=main_inputs
                                           )

        with output_column:
            bs_tab, mc_tab = st.tabs(["Black-Scholes Option Pricing", "Monte Carlo Option Pricing"])

            with bs_tab:
                stage_bs_subtab(fixed_inputs, config=AppSettings, color_config=Colors)

            with mc_tab:
                stage_mc_subtab(fixed_inputs, config=AppSettings, color_config=Colors)
                
    with tab_3:
        (
            _,
            candlestick_plot_column,
            _,
            modelling_data_column,
            _
        ) = uniform_columns(non_empty_column_sizes=[2,3])

        with candlestick_plot_column:
            selected_ticker, strike_price = render_candlestick_plot(key_prefix="tab_3_1", config=AppSettings, color_config=Colors)

        with modelling_data_column:
            stage_option_pricing(key_prefix="tab_3_2", 
                                 config=AppSettings,
                                 color_config=Colors, 
                                 selected_ticker=selected_ticker,
                                 strike_price=strike_price
                                 )

    remove_bottom_padding()

