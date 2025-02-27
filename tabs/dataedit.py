import streamlit as st
import pandas as pd
from datetime import date, datetime
import requests
import io

time = datetime.today().strftime('%Y-%m-%d %H-%M')

# Repository details
repo_url = st.secrets['forgejo']['repo_url']
api_base = st.secrets['forgejo']['api_base']
branch = "main"  # Adjust if the branch is different
auth = (st.secrets['forgejo']['username'], st.secrets['forgejo']['password'])
owner = st.secrets['forgejo']['owner']
repo = st.secrets['forgejo']['repo']


@st.cache_data
def get_json_file(file_path):
    """
    Fetch a JSON file from a Forgejo repository and return its data.

    Parameters:
    - file_path (str): Path to the JSON file in the repository.

    Returns:
    - dict: Dictionary of DataFrames.
    - None: If the fetch fails or the section is not found.
    """
    raw_url = f"{repo_url}/raw/{branch}/{file_path}"
    try:
        response = requests.get(raw_url, auth=auth)
        if response.status_code == 200:
            data = response.json()  # Parse JSON directly into a Python object
            # Return a dictionary of DataFrames
            dataframes = {}
            for key, value in data.items():
                df = pd.DataFrame(list(value.items()), columns=["Key", "Description"])
                dataframes[key] = df
            return dataframes
        else:
            st.error(f"Failed to fetch {file_path}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None


### THE PAGE BEGINS HERE ###

st.warning("Repare the commit functions to Forgejo repository")
st.write(time)

st.caption("Add your sample information dynamically")
st.caption("There are required fields")

if 'master' in st.session_state:
    master = st.session_state['master']
else:
    st.error("Master Inventory hasn't been loaded")

with st.status("Loading keys cheatsheet..."):
    naming_keys = get_json_file('acbc_database/documentation/naming_key.json')
    st.success("Loaded!!!")
with st.expander("See Naming Keys"):
    ckey1, ckey2 = st.columns((1, 1))
    with ckey1:
        st.dataframe(naming_keys['feedstock'], hide_index=True, use_container_width=True)
    with ckey2:
        st.dataframe(naming_keys['instrument'], hide_index=True, use_container_width=True)
        st.dataframe(naming_keys['researcher_initials'], hide_index=True, use_container_width=True)

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
            upload_url = f"{repo_url}/raw/{branch}/acbc_database/submitted_data/New-{researcher}-{time}.csv"
            response = requests.put(
                upload_url,
                data=csv_data,
                auth=auth
            )

            # Check if the upload was successful
            if response.status_code == 201:
                st.success("Submitted for review")
            else:
                st.error(f"Failed to upload file. Status code: {response.status_code}")
        else:
            st.error("The new sample dataframe is empty or no name set")

# Editing existing samples
st.header("Edit Current Data", divider='green')

samples_to_edit = st.multiselect(label='Select what samples you want to edit', options=master['ShortName'],
                                 max_selections=5, help="Only 5 at a time")

st.session_state.edited_df = st.data_editor(master[master['ShortName'].isin(samples_to_edit)], num_rows='fixed',
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
    st.dataframe(st.session_state.edited_df, hide_index=True)
    researcher = st.session_state['name']
    st.info(f"{st.session_state['name']} will upload for review the above edited dataframe after hitting submit.")
    submitted = st.form_submit_button("Submit for review")

    if submitted:
        if not st.session_state.edited_df.equals(master[master['ShortName'].isin(samples_to_edit)]):
            # Convert DataFrame to CSV in memory
            csv_buffer = io.StringIO()
            st.session_state.edited_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            upload_url = f"{repo_url}/raw/{branch}/acbc_database/submitted_data/Edited-{researcher}-{time}.csv"
            response = requests.put(
                upload_url,
                data=csv_data,
                auth=auth
            )

            # Check if the upload was successful
            if response.status_code == 201:
                st.success("Submitted for review")
            else:
                st.error(f"Failed to upload file. Status code: {response.status_code}")
        else:
            st.error("No changes have been detected")
