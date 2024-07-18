#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union

from datetime import date, timedelta

import time

import numpy as np
import pandas as pd
import jax.numpy as jnp

import streamlit as st
import streamlit.components.v1 as components
import altair as alt

import mechafil_jax.data as data
import mechafil_jax.sim as sim
import mechafil_jax.constants as C
import mechafil_jax.minting as minting
import mechafil_jax.date_utils as du

import scenario_generator.utils as u

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# local_css("debug.css")

@st.cache_data
def get_offline_data(start_date, current_date, end_date):
    PUBLIC_AUTH_TOKEN='Bearer ghp_EviOPunZooyAagPPmftIsHfWarumaFOUdBUZ'
    offline_data = data.get_simulation_data(PUBLIC_AUTH_TOKEN, start_date, current_date, end_date)

    _, hist_rbp = u.get_historical_daily_onboarded_power(current_date-timedelta(days=180), current_date)
    _, hist_rr = u.get_historical_renewal_rate(current_date-timedelta(days=180), current_date)
    _, hist_fpr = u.get_historical_filplus_rate(current_date-timedelta(days=180), current_date)

    smoothed_last_historical_rbp = float(np.median(hist_rbp[-30:]))
    smoothed_last_historical_rr = float(np.median(hist_rr[-30:]))
    smoothed_last_historical_fpr = float(np.median(hist_fpr[-30:]))

    return offline_data, smoothed_last_historical_rbp, smoothed_last_historical_rr, smoothed_last_historical_fpr


def plot_panel(scenario_results, baseline, start_date, current_date, end_date):
    # convert results dictionary into a dataframe so that we can use altair to make nice plots
    status_quo_results = scenario_results['status-quo']
    # col1 = st.columns(1)

    power_dff = pd.DataFrame()
    power_dff['RBP'] = status_quo_results['rb_total_power_eib']
    power_dff['QAP'] = status_quo_results['qa_total_power_eib']
    power_dff['Baseline'] = baseline
    power_dff['date'] = pd.to_datetime(du.get_t(start_date, end_date=end_date))

    minting_dff = pd.DataFrame()
    minting_dff['StatusQuo'] = status_quo_results['block_reward']
    minting_dff['date'] = pd.to_datetime(du.get_t(start_date, end_date=end_date))

    pledge_dff = pd.DataFrame()
    pledge_dff['StatusQuo'] = status_quo_results['day_pledge_per_QAP']
    pledge_dff['date'] = pd.to_datetime(du.get_t(start_date, forecast_length=pledge_dff.shape[0]))

    # supply_dff = pd.DataFrame()
    # supply_dff['StatusQuo'] = status_quo_results['circ_supply'] / 1_000_000
    # supply_dff['date'] = pd.to_datetime(du.get_t(start_date, end_date=end_date))
    
    supplyflow_dff = pd.DataFrame()
    # .diff().rolling(7).median() / 1_000_000
    supplyflow_dff['StatusQuo'] = status_quo_results['circ_supply']
    supplyflow_dff['StatusQuo'] = supplyflow_dff['StatusQuo'].diff().rolling(7).median().dropna() / 1_000_000
    supplyflow_dff['date'] = pd.to_datetime(du.get_t(start_date, forecast_length=supplyflow_dff.shape[0]))
    
    # with col1:
    # power_df = pd.melt(power_dff, id_vars=["date"], 
    #                     value_vars=[
    #                         "Baseline", 
    #                         "RBP", "QAP",],
    #                     #    "RBP-Pessimistic", "QAP-Pessimistic",
    #                     #    "RBP-Optimistic", "QAP-Optimistic"], 
    #                     var_name='Power', 
    #                     value_name='EIB')
    # power_df['EIB'] = power_df['EIB']
    # power = (
    #     alt.Chart(power_df)
    #     .mark_line()
    #     .encode(x=alt.X("date", title="", axis=alt.Axis(labelAngle=-45)), 
    #             y=alt.Y("EIB").scale(type='log'), color=alt.Color('Power', legend=alt.Legend(orient="top", title=None)))
    #     .properties(title="Network Power")
    #     .configure_title(fontSize=14, anchor='middle')
    # )
    # st.altair_chart(power.interactive(), use_container_width=True) 

    # minting_df = pd.melt(minting_dff, id_vars=["date"],
    #                         value_vars=["StatusQuo"],#, "Pessimistic", "Optimistic"], 
    #                         var_name='Scenario', value_name='FILRate')
    # minting = (
    #     alt.Chart(minting_df)
    #     .mark_line()
    #     .encode(x=alt.X("date", title="", axis=alt.Axis(labelAngle=-45)), 
    #             y=alt.Y("FILRate", title='FIL/epoch'), color=alt.Color('Scenario', legend=None))
    #     .properties(title="Block Rewards")
    #     .configure_title(fontSize=14, anchor='middle')
    # )
    # st.altair_chart(minting.interactive(), use_container_width=True)

    # pledge_per_qap_df = pd.melt(pledge_dff, id_vars=["date"],
    #                             value_vars=["StatusQuo"],#, "Pessimistic", "Optimistic"], 
    #                             var_name='Scenario', value_name='FIL')
    # day_pledge_per_QAP = (
    #     alt.Chart(pledge_per_qap_df)
    #     .mark_line()
    #     .encode(x=alt.X("date", title="", axis=alt.Axis(labelAngle=-45)), 
    #             y=alt.Y("FIL"), color=alt.Color('Scenario', legend=None))
    #     .properties(title="Pledge/32GiB QAP")
    #     .configure_title(fontSize=14, anchor='middle')
    # )
    # st.altair_chart(day_pledge_per_QAP.interactive(), use_container_width=True)

    # supply_df = pd.melt(supply_dff, id_vars=["date"],
    #                             value_vars=["StatusQuo"],
    #                             var_name='Scenario', value_name='M-FIL')
    # supply = (
    #     alt.Chart(supply_df)
    #     .mark_line()
    #     .encode(x=alt.X("date", title="", axis=alt.Axis(labelAngle=-45)), 
    #             y=alt.Y("M-FIL"), color=alt.Color('Scenario', legend=None))
    #     .properties(title="Circulating Supply")
    #     .configure_title(fontSize=14, anchor='middle')
    # )
    # st.altair_chart(supplyflow.interactive(), use_container_width=True)

    
    supplyflow_df = pd.melt(supplyflow_dff, id_vars=["date"],
                                value_vars=["StatusQuo"],
                                var_name='Scenario', value_name='M-FIL')
    supplyflow = (
        alt.Chart(supplyflow_df)
        .mark_line()
        .encode(x=alt.X("date", title="", axis=alt.Axis(labelAngle=-45)), 
                y=alt.Y("M-FIL"), color=alt.Color('Scenario', legend=None))
        .properties(title="2024 Simulation: Net Supply Change Per Day")
        .configure_title(fontSize=14, anchor='middle')
    )
    st.altair_chart(supplyflow.interactive(), use_container_width=True)


def add_costs(results_dict, cost_scaling_constant=0.1, filp_scaling_cost_pct=0.5):
    # (returns*multiplier - cost)/(pledge*multiplier)
    # TODO: allow user to configure these within reasonable bounds
    # cost_scaling_constant = 0.1
    # filp_scaling_cost_pct = 0.5

    # compute costs for the FIL+ case
    multiplier = 10
    rps = results_dict['1y_return_per_sector']
    dppq = results_dict['day_pledge_per_QAP'][0:len(rps)]
    
    filp_roi_scaling_costs = dppq*multiplier*cost_scaling_constant
    filp_roi_total_costs = filp_roi_scaling_costs/filp_scaling_cost_pct
    roi_fixed_costs = filp_roi_total_costs - filp_roi_scaling_costs
    results_dict['FIL+'] = 100*(rps*multiplier - filp_roi_total_costs)/(dppq*multiplier)

    # relative to FIL+, compute costs for the CC case
    multiplier = 1
    cc_roi_scaling_costs = dppq*multiplier*cost_scaling_constant
    cc_roi_total_costs = cc_roi_scaling_costs + roi_fixed_costs
    results_dict['CC'] = 100*(rps*multiplier - cc_roi_total_costs)/(dppq*multiplier)
    return results_dict

def run_sim(rbp, rr, fpr, lock_target, start_date, current_date, forecast_length_days, sector_duration_days, burn_boost, offline_data, 
            cost_scaling_constant=0.1, filp_scaling_cost_pct=0.5):
    simulation_results = sim.run_sim(
        rbp,
        rr,
        fpr,
        lock_target,

        start_date,
        current_date,
        forecast_length_days,
        sector_duration_days,
        burn_boost,
        offline_data
    )
    # simulation_results = add_costs(simulation_results, cost_scaling_constant, filp_scaling_cost_pct)
    # pib_per_sector = C.PIB / C.SECTOR_SIZE
    simulation_results['block_reward'] = simulation_results['day_network_reward'] / float(5*2880)
    # # compute yearly cumulative returns
    # pledge = simulation_results['day_pledge_per_QAP']
    # rps = simulation_results['1y_return_per_sector']
    # rpp = rps * pib_per_sector
    # simulation_results['1y_return_per_pib'] = rpp
    # days_1y = 365
    # yearly_returns_df = pd.DataFrame({
    #     'date': [
    #         str(current_date), 
    #         str(current_date+timedelta(days=365*1)), 
    #         str(current_date+timedelta(days=365*2)), 
    #         str(current_date+timedelta(days=365*3)),
    #         str(current_date+timedelta(days=365*4)),
    #         str(current_date+timedelta(days=365*5)),
    #     ],
    #     '1y_return_per_pib': [
    #         float(rpp[0]), 
    #         float(rpp[days_1y]), 
    #         float(rpp[days_1y*2]),  
    #         float(rpp[days_1y*3]), 
    #         float(rpp[days_1y*4]), 
    #         float(rpp[days_1y*5]), 
    #     ],
    # })
    return simulation_results #, yearly_returns_df

def forecast_economy(start_date=None, current_date=None, end_date=None, forecast_length_days=365*6):
    t1 = time.time()
    
    rb_onboard_power_pib_day =  st.session_state['rbp_slider']
    renewal_rate_pct = st.session_state['rr_slider']
    fil_plus_rate_pct = st.session_state['fpr_slider']
    # cost_scaling_constant = st.session_state['cost_scaling_constant']
    # filp_scaling_cost_pct = st.session_state['filp_scaling_cost_pct']

    lock_target = st.session_state['lock_target_slider']
    sector_duration_days = st.session_state['av_dur_slider']

    burn_boost = st.session_state['burn_factor_slider']

    # forecast_length_days=st.session_state['forecast_length_slider']
    # end_date = current_date + timedelta(days=forecast_length_days)
    
    # get offline data
    t2 = time.time()
    offline_data, _, _, _ = get_offline_data(start_date, current_date, end_date)
    t3 = time.time()
    # d.debug(f"Time to get historical data: {t3-t2}")

    # run simulation for the configured scenario, and for a pessimsitc and optimistic version of it
    # scenario_scalers = [0.5, 1.0, 1.5]
    # scenario_strings = ['pessimistic', 'status-quo', 'optimistic']
    scenario_scalers = [1.0]
    scenario_strings = ['status-quo']
    scenario_results = {}
    for ii, scenario_scaler in enumerate(scenario_scalers):
        rbp_val = rb_onboard_power_pib_day * scenario_scaler
        rr_val = max(0.0, min(1.0, renewal_rate_pct / 100. * scenario_scaler))
        fpr_val = max(0.0, min(1.0, fil_plus_rate_pct / 100. * scenario_scaler))

        rbp = jnp.ones(forecast_length_days) * rbp_val
        rr = jnp.ones(forecast_length_days) * rr_val
        fpr = jnp.ones(forecast_length_days) * fpr_val
        
        simulation_results = run_sim(rbp, rr, fpr, lock_target, start_date, current_date, forecast_length_days, sector_duration_days,burn_boost, offline_data) 
                #cost_scaling_constant=cost_scaling_constant, filp_scaling_cost_pct=filp_scaling_cost_pct)
        scenario_results[scenario_strings[ii]] = simulation_results

    baseline = minting.compute_baseline_power_array(
        np.datetime64(start_date), np.datetime64(end_date), offline_data['init_baseline_eib'],
    )

    # plot
    plot_panel(scenario_results, baseline, start_date, current_date, end_date)
    t4 = time.time()
    # d.debug(f"Time to forecast: {t4-t3}")
    # d.debug(f"Total Time: {t4-t1}")

def forecast_len():
    forecast_length_days=st.session_state['forecast_length_slider']
    return forecast_length_days

def main():
    st.set_page_config(
        page_title="Filecoin Net Supply Explorer",
        page_icon="🚀",  # TODO: can update this to the FIL logo
        layout="wide",
    )
    current_date = date.today() - timedelta(days=3)
    # mo_start = max(current_date.month - 1 % 12, 1)
    mo_start = max(current_date.month +1 % 12, 1)
    start_date = date(current_date.year, mo_start, 1)

    forecast_length_days=(365*1)
    end_date = current_date + timedelta(days=forecast_length_days)
    
    forecast_kwargs = {
        'start_date': start_date,
        'current_date': current_date,
        'end_date': end_date,
        'forecast_length_days': forecast_length_days,
    }

    _, smoothed_last_historical_rbp, smoothed_last_historical_rr, smoothed_last_historical_fpr = get_offline_data(start_date, current_date, end_date)
    smoothed_last_historical_renewal_pct = int(smoothed_last_historical_rr * 100)
    smoothed_last_historical_fil_plus_pct = int(smoothed_last_historical_fpr * 100)
    # d.debug('rbp:%0.02f, rr:%d, fpr:%d' % (smoothed_last_historical_rbp, smoothed_last_historical_rr, smoothed_last_historical_fpr))
    # d.debug(smoothed_last_historical_rbp)
    # d.debug(smoothed_last_historical_renewal_pct)
    # d.debug(smoothed_last_historical_fil_plus_pct)

    with st.sidebar:
        st.title('Filecoin Net Supply Explorer')

        # st.slider("Forecast Length", min_value=365, max_value=3650, value=720, step=100, format='%i', key="forecast_length_slider",
        #         on_change=forecast_len, disabled=False, label_visibility="visible")
        st.slider("Raw Byte Onboarding (PiB/day)", min_value=1., max_value=50., value=smoothed_last_historical_rbp, step=.1, format='%0.02f', key="rbp_slider",
                on_change=forecast_economy, kwargs=forecast_kwargs, disabled=False, label_visibility="visible")
        st.slider("Renewal Rate (Percentage)", min_value=10, max_value=99, value=95, step=1, format='%d', key="rr_slider",
                on_change=forecast_economy, kwargs=forecast_kwargs, disabled=False, label_visibility="visible")
        st.slider("FIL+ Rate (Percentage)", min_value=10, max_value=99, value=smoothed_last_historical_fil_plus_pct, step=1, format='%d', key="fpr_slider",
                on_change=forecast_economy, kwargs=forecast_kwargs, disabled=False, label_visibility="visible")
        st.slider("Lock Target (Percentage)", min_value=0.1, max_value=0.9, value=0.3, step=0.01, format='%.2f', key="lock_target_slider",
                on_change=forecast_economy, kwargs=forecast_kwargs, disabled=False, label_visibility="visible")
        st.slider("Average Sector Duration (Days)", min_value=180, max_value=540, value=360, step=10, format='%d', key="av_dur_slider",
                on_change=forecast_economy, kwargs=forecast_kwargs, disabled=False, label_visibility="visible")
        st.slider("Burn Factor (Multiplicative)", min_value=0.1, max_value=10., value=1., step=0.1, format='%.2f', key="burn_factor_slider",
                on_change=forecast_economy, kwargs=forecast_kwargs, disabled=False, label_visibility="visible")


        
        st.button("Forecast", on_click=forecast_economy, kwargs=forecast_kwargs, key="forecast_button")

    
    # if "debug_string" in st.session_state:
    #     st.markdown(
    #         f'<div class="debug">{ st.session_state["debug_string"]}</div>',
    #         unsafe_allow_html=True,
    #     )
    # components.html(
    #     d.js_code(),
    #     height=0,
    #     width=0,
    # )

if __name__ == '__main__':
    main()
