import streamlit as st
import pandas as pd
from pricing import black_scholes_price, compute_greeks
from plotting import create_basic_option_graph, create_greek_graph
from config import asset_price_slider, strike_price_slider, time_input, non_risk_interest_input, volatility_input

st.set_page_config(page_title="Option Pricing App", layout="wide")
tab1, tab2, tab3 = st.tabs(["Mathematical background", "Option price calculator", "3rd page"])

with tab1:
    st.title("The math behind the famous Black-Scholes formula")


with tab2:
    st.title("Black-Scholes Option Pricing")

    void1, params_slider, void2, output, void3, greeks, void4 = st.columns([0.25, 1.5, 0.25, 1.5, 0.25, 0.5, 0.25])

    with params_slider:

        for _ in range(5):
            st.write("")
            
        st.subheader("Parameters")

        S = st.slider(asset_price_slider.label,
                      min_value=asset_price_slider.min, value=asset_price_slider.default,
                      max_value=asset_price_slider.max,
                      step=asset_price_slider.step, format="%2f €")
        
        K = st.slider(strike_price_slider.label,
                      min_value=strike_price_slider.min, value=strike_price_slider.default,
                      max_value=strike_price_slider.max,
                      step=strike_price_slider.step, format="%2f €")

        params_void1, params_middle_loc, params_void2 = st.columns([1, 1.5, 1])

        with params_middle_loc:

            T = st.number_input(time_input.label, 
                                min_value=time_input.min, value=time_input.default, 
                                max_value=time_input.max, step=time_input.step)
            
            r = st.number_input(non_risk_interest_input.label, 
                                min_value=non_risk_interest_input.min, value=non_risk_interest_input.default, 
                                max_value= non_risk_interest_input.max, step=non_risk_interest_input.step)

            sigma = st.number_input(volatility_input.label, 
                                    min_value=volatility_input.min, max_value=volatility_input.max, 
                                    value=volatility_input.default, step=volatility_input.step)
        
            middle_void1, option_type_loc, middle_void2 = st.columns([1, 2.1, 1])

            with option_type_loc: 
                option_type = st.segmented_control("Option Type", ["Call", "Put"], selection_mode="single", default="Call")

    with output:
        st.subheader("Option Price")
        price = black_scholes_price(S, K, T, r, sigma, option_type)
        st.success(f"{option_type} option price: {price:.2f}€")

        output_void1, output_coloring, output_void2 = st.columns([0.75, 1.25, 0.75])
        
        with output_coloring:
            color_toggle = st.toggle("Toggle coloring of areas", value=True)
            bs_function_toggle = st.toggle("Toggle Black-Scholes price function", value=True)
        st.plotly_chart(create_basic_option_graph(S, K, asset_price_slider.max, strike_price_slider.max,
                                                  price, option_type, T, r, sigma, color_toggle, bs_function_toggle),
                        use_container_width=True)

    with greeks:

        graph_placeholder = st.empty()

        greeks = pd.DataFrame(compute_greeks(S, K, T, r, sigma, option_type), index = [0])
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

        graph_placeholder.plotly_chart(create_greek_graph(selected_variable, S, K, T, r, sigma, option_type, selected_greek),
                          use_container_width=True, config={'displayModeBar': False})