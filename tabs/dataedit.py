import streamlit as st
import pandas as pd
from datetime import date, datetime
import requests
from requests.auth import HTTPBasicAuth
import io

NEXTCLOUD_URL = st.secrets["nextcloud"]["NEXTCLOUD_URL"]
USERNAME = st.secrets["nextcloud"]["username"]
PASSWORD = st.secrets["nextcloud"]["next_cloudpass"]
time = datetime.today().strftime('%Y-%m-%d %H-%M')
newsample_url = f"{NEXTCLOUD_URL}/NEWSAMPLES"

### THE PAGE BEGINS HERE ###
st.write(time)

st.caption("Add your sample information dynamically")
st.caption("There are required fields")

if 'master' in st.session_state:
    master = st.session_state['master']
else:
    st.error("Master Inventory hasn't been loaded")

NEXTCLOUD_URL = st.secrets["nextcloud"]["NEXTCLOUD_URL"]
USERNAME = st.secrets["nextcloud"]["username"]
PASSWORD = st.secrets["nextcloud"]["next_cloudpass"]


@st.cache_data
def get_excel_file_as_dataframe(file_path, header=0, sheet_name=None):
    url = f"{NEXTCLOUD_URL}{file_path}"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            df = pd.read_excel(io.BytesIO(response.content), header=header, sheet_name=sheet_name, engine='openpyxl')
            return df
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to Load the master: {e}")
        return []


with st.status("Loading keys cheatsheet..."):
    biosourcekey = get_excel_file_as_dataframe('/DOCUMENTATION/naming_key.xlsx', sheet_name='table1')
    instrumentkey = get_excel_file_as_dataframe('/DOCUMENTATION/naming_key.xlsx', sheet_name='table2')
    researcherkey = get_excel_file_as_dataframe('/DOCUMENTATION/naming_key.xlsx', sheet_name='table3')

    st.success("Loaded!!!")
with st.expander("See Naming Keys"):
    ckey1, ckey2 = st.columns((1, 1))
    with ckey1:
        st.dataframe(biosourcekey, hide_index=True, use_container_width=True)
    with ckey2:
        st.dataframe(instrumentkey, hide_index=True, use_container_width=True)
        st.dataframe(researcherkey, hide_index=True, use_container_width=True)

### SUBMITTING NEW SAMPLES WITH A FORM ###

st.header("Submit New Data", divider='green')
new_data_df = pd.DataFrame(columns=master.columns)
st.session_state.new_data_df2 = st.data_editor(new_data_df, num_rows='dynamic', hide_index=True,
                                               column_config={
                                                   "ProjectCode": st.column_config.TextColumn(disabled=True,
                                                                                              help='Automatically added'),
                                                   "ShortName": st.column_config.TextColumn(help='XXX####_XX###',
                                                                                            max_chars=13,
                                                                                            required=True),
                                                   "LongName": st.column_config.TextColumn(help='Max 30 chars',
                                                                                           max_chars=30,
                                                                                           required=False),
                                                   "DateProduced": st.column_config.DateColumn(
                                                       min_value=date(1980, 1, 1),
                                                       format="YYYY-MM-DD",
                                                       step=1, required=True),
                                                   "Feedstock": st.column_config.TextColumn(help='Max 30 chars',
                                                                                            max_chars=30,
                                                                                            required=True),
                                                   "Researcher/Student": st.column_config.TextColumn(
                                                       help='Max 30 chars',
                                                       max_chars=30,
                                                       required=True),
                                                   "GroupLab": st.column_config.SelectboxColumn(
                                                       options=["Hawboldt", "McGuire", "Poduska"],
                                                       required=True),
                                                   "PyrolysisType": st.column_config.SelectboxColumn(
                                                       options=["Fast", "Slow"],
                                                       required=True),
                                                   "Temp(C)": st.column_config.NumberColumn(required=True,
                                                                                            min_value=-273.15),
                                                   "ProcessDetails": st.column_config.TextColumn(
                                                       help='rate: #deg/min, temp: #deg, hold: #min | rate:nat-cooling, temp:room',
                                                       max_chars=100,
                                                       required=True),
                                                   "UnitType": st.column_config.TextColumn(help='US',
                                                                                           max_chars=5,
                                                                                           required=True),
                                                   "Capacity(mg/g)": st.column_config.NumberColumn(),
                                                   "Static/Dynamic": st.column_config.SelectboxColumn(
                                                       options=["Static", "Dynamic"]),
                                                   "BET(m2/g)": st.column_config.NumberColumn(),
                                                   "pH": st.column_config.NumberColumn(min_value=0, max_value=14),
                                                   "Yield(%)": st.column_config.NumberColumn(),
                                                   "PoreSize(units)": st.column_config.NumberColumn(),
                                                   "PoreVolume(units)": st.column_config.NumberColumn(),
                                                   "%C": st.column_config.NumberColumn(min_value=0, max_value=100),
                                                   "%H": st.column_config.NumberColumn(min_value=0, max_value=100),
                                                   "%N": st.column_config.NumberColumn(min_value=0, max_value=100),
                                                   "%O": st.column_config.NumberColumn(min_value=0, max_value=100),
                                                   "Density": st.column_config.NumberColumn(),
                                                   "Hydrophobicity": st.column_config.NumberColumn(),
                                                   "Notes": st.column_config.TextColumn(
                                                       help='Short description (Max 50 charts)',
                                                       max_chars=50,
                                                       required=False),
                                                   "Published?": st.column_config.LinkColumn(help='DOI link',
                                                                                             validate="^https://.+$")
                                               })

with st.form("new_data"):
    st.write("Inspect the dataframe you have just created")
    st.session_state.new_data_df2['ProjectCode'] = "ACBC" + st.session_state.new_data_df2['GroupLab'].str[0]
    st.write(st.session_state.new_data_df2)
    researcher = st.session_state['name']
    st.info(f"{st.session_state['name']} will upload for review the above dataframe after hitting submit.")
    submitted = st.form_submit_button("Submit for review")

    if submitted:
        if researcher is not None and not st.session_state.new_data_df2.empty:
            # Convert DataFrame to CSV in memory
            csv_buffer = io.StringIO()
            st.session_state.new_data_df2.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            upload_url = f'{newsample_url}/{researcher}-{time}.csv'
            response = requests.put(
                upload_url,
                data=csv_data,
                auth=HTTPBasicAuth(USERNAME, PASSWORD)
            )

            # Check if the upload was successful
            if response.status_code == 201:
                st.success("Submitted for review")
            else:
                st.error(f"Failed to upload file. Status code: {response.status_code}")
        else:
            st.error("The new sample dataframe is empty or no name set")

st.header("Edit Current Data", divider='green')

samples_to_edit = st.multiselect(label='Select what samples you want to edit', options=master['ShortName'],
                                 max_selections=5, help="Only 5 at a time")

st.session_state.edited_df = st.data_editor(master[master['ShortName'].isin(samples_to_edit)], num_rows='dynamic',
                                            hide_index=True,
                                            column_config={
                                                "ProjectCode": st.column_config.TextColumn(disabled=True,
                                                                                           help='Automatically added'),
                                                "ShortName": st.column_config.TextColumn(help='XXX####_XX###',
                                                                                         max_chars=13,
                                                                                         required=True),
                                                "LongName": st.column_config.TextColumn(help='Max 30 chars',
                                                                                        max_chars=30,
                                                                                        required=False),
                                                "DateProduced": st.column_config.DateColumn(
                                                    min_value=date(1980, 1, 1),
                                                    format="YYYY-MM-DD",
                                                    step=1, required=True, disabled=True),
                                                "Feedstock": st.column_config.TextColumn(help='Max 30 chars',
                                                                                         max_chars=30,
                                                                                         required=True),
                                                "Researcher/Student": st.column_config.TextColumn(
                                                    help='Max 30 chars',
                                                    max_chars=30,
                                                    required=True),
                                                "GroupLab": st.column_config.SelectboxColumn(
                                                    options=["Hawboldt", "McGuire", "Poduska"],
                                                    required=True),
                                                "PyrolysisType": st.column_config.SelectboxColumn(
                                                    options=["Fast", "Slow"],
                                                    required=True),
                                                "Temp(C)": st.column_config.NumberColumn(required=True,
                                                                                         min_value=-273.15),
                                                "ProcessDetails": st.column_config.TextColumn(
                                                    help='rate: #deg/min, temp: #deg, hold: #min | rate:nat-cooling, temp:room',
                                                    max_chars=100,
                                                    required=True),
                                                "UnitType": st.column_config.TextColumn(help='US',
                                                                                        max_chars=5,
                                                                                        required=True),
                                                "Capacity(mg/g)": st.column_config.NumberColumn(),
                                                "Static/Dynamic": st.column_config.SelectboxColumn(
                                                    options=["Static", "Dynamic"]),
                                                "BET(m2/g)": st.column_config.NumberColumn(),
                                                "pH": st.column_config.NumberColumn(min_value=0, max_value=14),
                                                "Yield(%)": st.column_config.NumberColumn(),
                                                "PoreSize(units)": st.column_config.NumberColumn(),
                                                "PoreVolume(units)": st.column_config.NumberColumn(),
                                                "%C": st.column_config.NumberColumn(min_value=0, max_value=100),
                                                "%H": st.column_config.NumberColumn(min_value=0, max_value=100),
                                                "%N": st.column_config.NumberColumn(min_value=0, max_value=100),
                                                "%O": st.column_config.NumberColumn(min_value=0, max_value=100),
                                                "Density": st.column_config.NumberColumn(),
                                                "Hydrophobicity": st.column_config.NumberColumn(),
                                                "Notes": st.column_config.TextColumn(
                                                    help='Short description (Max 50 charts)',
                                                    max_chars=50,
                                                    required=False, disabled=True),
                                                "Published?": st.column_config.LinkColumn(help='DOI link',
                                                                                          validate="^https://.+$",
                                                                                          disabled=True)
                                            })

with st.form("edited_data"):
    st.write("Inspect the dataframe you have just edited")
    st.write(st.session_state.edited_df)
    researcher = st.session_state['name']
    st.info(f"{st.session_state['name']} will upload for review the above edited dataframe after hitting submit.")
    submitted = st.form_submit_button("Submit for review")

    if submitted:
        if not st.session_state.edited_df.equals(master[master['ShortName'].isin(samples_to_edit)]):
            # Convert DataFrame to CSV in memory
            csv_buffer = io.StringIO()
            st.session_state.edited_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            upload_url = f'{newsample_url}/Edited-{researcher}-{time}.csv'
            response = requests.put(
                upload_url,
                data=csv_data,
                auth=HTTPBasicAuth(USERNAME, PASSWORD)
            )

            # Check if the upload was successful
            if response.status_code == 201:
                st.success("Submitted for review")
            else:
                st.error(f"Failed to upload file. Status code: {response.status_code}")
        else:
            st.error("No changes have been detected")
