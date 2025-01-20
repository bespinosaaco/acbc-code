import streamlit as st
import pandas as pd
from datetime import date, datetime

st.warning("Page under work ⚒️!")
st.caption("Add your sample information dynamically")
st.caption("There are required fields")

if 'master' in st.session_state:
    master = st.session_state['master']
else:
    st.error("Master Inventory hasn't load")

### SUBMITTING NEW SAMPLES WITH A FORM ###

new_data_df = pd.DataFrame(columns=master.columns)
st.session_state.new_data_df2 = st.data_editor(new_data_df,num_rows='dynamic',hide_index=True,
                              column_config={
                                    "SampleCode":st.column_config.TextColumn(disabled=True,help='Disabled'),
                                    "DateProduced":st.column_config.DateColumn(
                                                    min_value=date(1980, 1, 1),
                                                    format="YYYY-MM-DD",
                                                    step=1),
                                    "GroupLab":st.column_config.SelectboxColumn(
                                                    options=["Kelly","McGuire","Poduska"],
                                                    required=True),
                                    "PyrolysisType": st.column_config.SelectboxColumn(
                                                    options=["Fast", "Slow"],
                                                    required=True),
                                    "Temp(C)":st.column_config.NumberColumn(),
                                    "Capacity(mg/g)":st.column_config.NumberColumn(),
                                    "BET(m2/g)":st.column_config.NumberColumn(),
                                    "pH":st.column_config.NumberColumn(min_value=0,max_value=14),
                                    "Yield(%)":st.column_config.NumberColumn(),
                                    "PoreSize(units)":st.column_config.NumberColumn(),
                                    "PoreVolume(units)":st.column_config.NumberColumn(),
                                    "%C":st.column_config.NumberColumn(min_value=0,max_value=100),
                                    "%H":st.column_config.NumberColumn(min_value=0, max_value=100),
                                    "%N":st.column_config.NumberColumn(min_value=0, max_value=100),
                                    "%O":st.column_config.NumberColumn(min_value=0, max_value=100),
                                    "Density":st.column_config.NumberColumn(),
                                    "Hydrophobicity":st.column_config.NumberColumn(),
                                    "Published?":st.column_config.LinkColumn(help='DOI link', validate="^https://.+$")
                              })

with st.form("new_data"):
    st.write("Inspect the dataframe")
    st.write(st.session_state.new_data_df2)
    submitted = st.form_submit_button("Submit for review")
    if submitted:
        st.success("Submitted for review")

st.write(datetime.today().strftime('%Y-%m-%d'))