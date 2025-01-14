import streamlit as st
import requests
import pandas as pd
import io
from requests.auth import HTTPBasicAuth
import plotly.graph_objects as go

NEXTCLOUD_URL = st.secrets["nextcloud"]["NEXTCLOUD_URL"]
USERNAME = st.secrets["nextcloud"]["username"]
PASSWORD = st.secrets["nextcloud"]["next_cloudpass"]

@st.cache_data
def get_csv_file_as_dataframe(file_path):
    url = f"{NEXTCLOUD_URL}{file_path}"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            csv_content = response.content.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            return df
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to Load the master: {e}")
        return []

###### The Dashboard begins here #######

st.title("AC/BC Visualization 🦦")
st.caption("Scroll down to see all the interactives and downloadables graphics")

### Displaying the inventory
with st.spinner('Connecting to Brian NextCloud...'):
    if 'master' in st.session_state:
        master = st.session_state['master']
    else:
        master = get_csv_file_as_dataframe("/master.csv")
        st.session_state['master'] = master

    col_reload = st.columns([1, 0.1])
    with col_reload[0]:
        st.write('Connected to Brian NextCloud')
    with col_reload[1]:
        with st.spinner('Reloading'):
            if st.button('🔄️'):
                get_csv_file_as_dataframe.clear()
                master = get_csv_file_as_dataframe("/master.csv")
                st.session_state['master'] = master
        # This is to check if the reload button is working
        #         st.session_state['reload_count'] = st.session_state.get('reload_count', 0) + 1
        #
        # st.write(f"Reload count: {st.session_state.get('reload_count', 0)}")

    st.write('''
    ### Master Biochar Inventory 📖
    ''')
    st.caption('This is the Biochar Inventory. You can sort, search, expand and download')
    st.dataframe(master,use_container_width=True)

### Pulling Data from the inventory

with st.form("pull_data"):
    st.write('''
        ### Visualize information from the selected samples 👇 
        ''')

    par1, par2 = st.columns((1, 1))
    ### Sample and param
    with par1:
        choice = st.multiselect('Select sample(s)', options=master['SampleCode'], placeholder='SampleCode',
                                help='Select the samples you wish to compare')
    with par2:
        param = st.selectbox('Parameter', options=['Capacity(mg/g)', 'BET(m2/g)', 'pH', 'Yield (%)', 'PoreSize(units)',
                                                   'PoreVolume(units)', 'Density ', 'Hydrophobicity '],
                             help='Select one of the parameters',
                             placeholder='Parameter')
    submitted =st.form_submit_button("Visualize")
    st.markdown('''---''')
    if submitted:
        col1, col2, col3 = st.columns((2, 2, 4))
        col4, col5 = st.columns((1, 1))

        ### Selected samples sortable dataframe
        with col1:
            st.dataframe(master[['SampleCode','LongName', param]][master['SampleCode'].isin(choice)],
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
                go.Bar(name='Sample Data', x=choice, y=master[param][master['SampleCode'].isin(choice)])
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
            df = master[['SampleCode', '%C', '%H', '%N', '%O']][master['SampleCode'].isin(choice)]
            fig = go.Figure()

            for element in ['%C', '%H', '%N', '%O']:
                fig.add_trace(go.Bar(
                    x=df['SampleCode'],
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

    ad_df = master.loc[:,['LongName','Capacity(mg/g)','BET(m2/g)']]
    ad_df['(O+N)/C'] = ((master['%O']+master['%N'])/master['%C'])
    ad_df.dropna(axis=0,how='any',inplace=True)

    labels = [(f"{master.loc[i,'SampleCode']}: ({ad_df['Capacity(mg/g)'].iloc[i]:.2f},"
               f" {ad_df['BET(m2/g)'].iloc[i]:.2f},"
               f" {ad_df['(O+N)/C'].iloc[i]:.2f})") for i in range(len(ad_df))]
    ads_col1,ads_col2 =st.columns((1,2))
    with ads_col1:
        st.dataframe(ad_df)
    with ads_col2:
        fig = go.Figure(data=[go.Scatter3d(
            x=ad_df['(O+N)/C'],
            y=ad_df['BET(m2/g)'],
            z=ad_df['Capacity(mg/g)'],
            mode='markers',
            marker=dict(
                size=5,
                color=ad_df['Capacity(mg/g)'],  # Color by z values
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
