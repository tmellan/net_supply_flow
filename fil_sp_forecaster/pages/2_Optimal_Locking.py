import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

def xr(locking_pct_change, xr_locking_sensitivity):
    return 1 + locking_pct_change * xr_locking_sensitivity / 100
    
def pledge(pledge0, locking_pct_change):
    return pledge0 * (1 + locking_pct_change / 100)
    
def locking_pct_change(TL):
    return 100 * (TL / 30 - 1)
    
def ROI(reward, pledge, cost, xr, pct_fiat_cost):
    return 100 * (xr * reward - 0.01 * cost * reward * (pct_fiat_cost / 100 + (1 - pct_fiat_cost / 100) * xr)) / (xr * pledge)
    
TL_values = np.linspace(30, 90, 100)  # Define the range of TL values for plotting

def plot_ROI():
    CostPCTofRewards = st.session_state['cost_pct_rewards']
    XRLockSensitivity = st.session_state['xr_locking_sensitivity']
    PCTCostInFiat = st.session_state['pct_fiat_cost']

    # CostPCTofRewards = 90
    # XRLockSensitivity = 10
    # PCTCostInFiat = 80
    
    ROI_values_2 = [ROI(0.1, pledge(0.2, locking_pct_change(TL)), CostPCTofRewards, xr(locking_pct_change(TL), XRLockSensitivity), PCTCostInFiat)
                    - ROI(0.1, pledge(0.2, locking_pct_change(30)), CostPCTofRewards, xr(locking_pct_change(30), XRLockSensitivity), PCTCostInFiat)
                    for TL in TL_values]
    
    plot_df = pd.DataFrame()
    plot_df['TL'] = TL_values
    # plot_df['ROI (ref)'] = ROI_values_1
    plot_df['ROI (cfg)'] = ROI_values_2
    
    plot_df = plot_df.melt('TL', var_name='ROI', value_name='Value')
    chart = alt.Chart(plot_df).mark_line().encode(
        x=alt.X('TL', title='% of supply locked'),
        y=alt.Y('Value', title='% change'),
        # color='ROI'
    ).properties(
        width=800,
        height=400,
        title="Return on Collateral"
    )
    st.altair_chart(chart)
    
st.set_page_config(
    page_title="Optimal",
    page_icon="🚀",  # TODO: can update this to the FIL logo
    layout="wide",
)

with st.sidebar:
    st.slider(
        "SP costs as a \% of rewards", min_value=50, max_value=95, value=90, step=1, key="cost_pct_rewards",
        on_change=plot_ROI
    )
    st.slider(
        "\% of costs in paid in fiat", min_value=50, max_value=95, value=80, step=1, key="pct_fiat_cost",
        on_change=plot_ROI
    )
    st.slider(
        "XR locking sensitivity", min_value=1, max_value=25, value=10, step=1, key="xr_locking_sensitivity",
        on_change=plot_ROI
    )
    st.button("Run", on_click=plot_ROI)
