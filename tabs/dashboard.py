import streamlit as st
import requests
import pandas as pd
import io
import plotly.graph_objects as go
import xml.etree.ElementTree as ET

# Repository details
repo_url = st.secrets['forgejo']['repo_url']
api_base = st.secrets['forgejo']['api_base']
branch = "main"  # Adjust if the branch is different
auth = (st.secrets['forgejo']['username'], st.secrets['forgejo']['password'])
owner = st.secrets['forgejo']['owner']
repo = st.secrets['forgejo']['repo']


###### Function section begins here #######

@st.cache_data
def fetch_csv(file_path, header=0):
    """
    Function to fetch csv spreadsheets

    Parameters:
        -file_path(str): The path to the subfolder (e.g., 'master.csv').
        -header(int or None): Indicate the index of the csv headers. Default = 0
    Returns:
        -pandas.dataframe: The csv file as a Pandas DataFrame
    """
    raw_url = f"{repo_url}/raw/{branch}/{file_path}"
    try:
        response = requests.get(raw_url, auth=auth)
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.content.decode('utf-8')), header=header)
        else:
            st.error(f"Failed to fetch {file_path}. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


@st.cache_data
def list_files(subfolder_path):
    """
    Lists all files in the specified subfolder of the Forgejo repository.

    Parameters:
    - subfolder_path (str): The path to the subfolder (e.g., 'acbc_database').

    Returns:
    - list: A list of file paths (relative to the repository root) in the subfolder.
    """
    url = f"{api_base}/repos/{owner}/{repo}/contents/{subfolder_path}?ref={branch}"
    try:
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            contents = response.json()
            # st.write(contents) #Uncomment to see the
            return [item['name'] for item in contents if item['type'] == 'file']
        else:
            st.error(f"Failed to list files. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error listing files: {e}")
        return []


def plot_line_chart(data, title="Line Chart", xaxis_title="X Axis", yaxis_title="Y Axis"):
    """
    Create a simple line chart using Plotly.

    Parameters:
    - data (df): dataframe with the data
    - title (str): The title of the chart.
    - xaxis_title (str): The label for the x-axis.
    - yaxis_title (str): The label for the y-axis.

    Returns:
    - go.Figure: A Plotly figure object representing the line chart.
    """
    fig = go.Figure(data=go.Scatter(
        x=data.iloc[:, 0],
        y=data.iloc[:, 1],
        mode='lines',
        name='line',
        line=dict(color='blue', width=2)
    ))

    # Update layout for better visualization
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        autosize=False,
        width=800,
        height=500,
        margin=dict(l=50, r=50, b=100, t=100, pad=4)
    )

    return fig


###### The Dashboard page begins here #######

st.title("AC/BC Visualization 🦦")
st.header(f"Welcome back {st.session_state['name']}")
st.caption("Scroll down to see all the interactives and downloadables graphics")

### Loading Inventory from Database
with st.status('Connecting to ACBC-REPO...'):
    if 'master' in st.session_state:
        master = st.session_state['master']
    else:
        master = fetch_csv("acbc_database/master.csv")
        master.dropna(axis=0, how='all', inplace=True)
        st.session_state['master'] = master

    if 'UCD_Database' in st.session_state:
        UCD_Database = st.session_state['UCD_Database']
    else:
        UCD_Database = fetch_csv("uc_davis_database/UC_Davis_Biochar_Database.csv")
        UCD_Database.dropna(axis=0, how='all', inplace=True)
        st.session_state['UCD_Database'] = UCD_Database

    col_reload = st.columns([1, 0.1])
    with col_reload[0]:
        st.success('Connected to ACBC-REPO')
    with col_reload[1]:
        with st.spinner('Reloading'):
            if st.button('🔄️', key='file_refresh'):
                fetch_csv.clear()
                master = fetch_csv("acbc_database/master.csv")
                st.session_state['master'] = master
        # This is to check if the reload button is working
        #         st.session_state['reload_count'] = st.session_state.get('reload_count', 0) + 1
        #
        # st.write(f"Reload count: {st.session_state.get('reload_count', 0)}")

### Displaying the inventory
st.write('''
### Master Biochar Inventory 📖
''')
st.caption('This is the Biochar Inventory. You can sort, search, expand and download')
st.dataframe(master, use_container_width=True)

with st.expander("See the UC Davis Database"):
    st.write("Visit UC Davis Database 👇")
    st.link_button("UC Davis Database", "https://biochar.ucdavis.edu/")
    st.dataframe(UCD_Database)

### Pulling Data from the inventory
with st.form("pull_data"):
    st.write('''
        ### Visualize information from the selected samples 👇 
        ''')

    par1, par2 = st.columns((1, 1))
    ### Sample and param
    with par1:
        choice = st.multiselect('Select sample(s)', options=master['ShortName'], placeholder='ShortName',
                                help='Select the samples you wish to compare')
    with par2:
        param = st.selectbox('Parameter', options=['Capacity(mmol/g)', 'BET(m2/g)', 'pH', 'Yield (%)', 'PoreSize(nm)',
                                                   'PoreVolume(cm3/g)', 'Density ', 'Hydrophobicity '],
                             help='Select one of the parameters',
                             placeholder='Parameter')
    submitted = st.form_submit_button("Visualize")
    st.markdown('''---''')
    if submitted:
        col1, col2, col3 = st.columns((2, 2, 4))
        col4, col5 = st.columns((1, 1))

        ### Selected samples sortable dataframe
        with col1:
            st.dataframe(master[['ShortName', 'LongName', param]][master['ShortName'].isin(choice)],
                         use_container_width=True)
        ### Selected parameter description
        with col2:
            st.write(f'''
                ### **{param} Method**
                Some description of the methodology used to record this data.
                Step-by-step:
                1. This is step 1
                2. This is step 2
                ''')
        ### The sample by selected parameter bar graph
        with col3:
            fig = go.Figure(data=[
                go.Bar(name='Sample Data', x=choice, y=master[param][master['ShortName'].isin(choice)])
            ])

            fig.update_layout(
                title=f'Sample by {param}',
                xaxis_title='Sample',
                yaxis_title=f'{param}',
                template='plotly_white'  # Optional: set the background to white for better readability
            )
            st.plotly_chart(fig, use_container_width=True)
        ### The samples elemental analysis stacked bar graph
        with col4:
            df = master[['ShortName', '%C', '%H', '%N', '%O']][master['ShortName'].isin(choice)]
            fig = go.Figure()

            for element in ['%C', '%H', '%N', '%O']:
                fig.add_trace(go.Bar(
                    x=df['ShortName'],
                    y=df[element],
                    name=element,
                    text=df[element].apply(lambda x: f'{x:.2f}%'),
                    textposition='auto'
                ))

            # Update layout
            fig.update_layout(
                barmode='stack',
                title='Elemental Analysis Composition',
                xaxis_title='Sample',
                yaxis_title='Percentage (%)',
            )
            st.plotly_chart(fig, use_container_width=True)

### Adsorption correlation scatter 3D plot
with st.container(border=False):
    st.write(r'''
    ---
    ### Adsorption vs SSA vs $(O+N)/C$  
    ''')

    ad_df = master.loc[:, ['ShortName', 'LongName', 'Capacity(mmol/g)', 'BET(m2/g)']]
    ad_df['(O+N)/C'] = ((master['%O'] + master['%N']) / master['%C'])
    ad_df.dropna(axis=0, subset=['Capacity(mmol/g)'], inplace=True)

    labels = [(f"{ad_df.iloc[i, 0]}: ({ad_df['Capacity(mmol/g)'].iloc[i]:.2f},"
               f"{ad_df['BET(m2/g)'].iloc[i]:.2f},"
               f"{ad_df['(O+N)/C'].iloc[i]:.2f})") for i in range(len(ad_df))]
    ads_col1, ads_col2 = st.columns((1, 2))
    with ads_col1:
        st.dataframe(ad_df)
    with ads_col2:
        fig = go.Figure(data=[go.Scatter3d(
            x=ad_df['(O+N)/C'],
            y=ad_df['BET(m2/g)'],
            z=ad_df['Capacity(mmol/g)'],
            mode='markers',
            marker=dict(
                size=5,
                color=ad_df['Capacity(mmol/g)'],  # Color by z values
                colorscale='Viridis',
                opacity=0.8),
            text=labels,  # Add labels for hover
            hoverinfo='text'  # Display only the text on hover

        )])

        # Customize layout
        fig.update_layout(
            paper_bgcolor="rgba(230, 230, 230, 0.8)",
            width=800,
            height=800,
            scene=dict(
                xaxis=dict(
                    title='(N+O)/C',
                    autorange=True
                ),
                yaxis=dict(
                    title='SSA(m^2/mg)',
                    autorange=True
                ),
                zaxis=dict(
                    title='Adsorption (mg/g)',
                    autorange=True
                )
            )
        )

        # 3D scatter plot
        st.plotly_chart(fig, use_container_width=True)

### Instrument Data Viz
st.write('''
    ---
    ### Visualize instrument data  👇 
    ''')
with st.container(border=False):
    data_file_sel = None
    inst_col1, inst_col2, inst_col3 = st.columns((1, 1, 0.1), vertical_alignment='bottom')
    with inst_col1:
        instrument_sel = st.selectbox(label='Select the instrument to display data',
                                      options=["infrared","x-ray"], placeholder="Instrument")
    with inst_col2:
        if instrument_sel:
            istrmt_file_list = list_files(f"acbc_database/data/{instrument_sel}")
            data_file_sel = st.selectbox(label=f"List of available {instrument_sel}", options=istrmt_file_list)
    with inst_col3:
        st.caption('Refresh')
        with st.spinner('Reloading'):
            if st.button('🔄️', key='filelist_refresh', type='secondary', use_container_width=True):
                list_files.clear()

    if st.button("Viz Spectrum"):
        viz_file_col1, viz_file_col2 = st.columns([1, 3])
        if data_file_sel is not None:
            file_df = fetch_csv(f"acbc_database/data/{instrument_sel}/{data_file_sel}", header=None)
            file_df.columns = ["X", "Y"]
            viz_file_col1.dataframe(file_df)
            viz_file_col2.plotly_chart(plot_line_chart(file_df, data_file_sel[:-4], 'Wavenumber', "Transmission"),
                                       use_container_width=True)
        else:
            st.warning("No data to pull")
