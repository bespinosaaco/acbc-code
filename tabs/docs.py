import streamlit as st
from streamlit import divider, caption
import requests
import pandas as pd
import io
from requests.auth import HTTPBasicAuth

NEXTCLOUD_URL = st.secrets["nextcloud"]["NEXTCLOUD_URL"]
USERNAME = st.secrets["nextcloud"]["username"]
PASSWORD = st.secrets["nextcloud"]["next_cloudpass"]

@st.cache_data
def get_excel_file_as_dataframe(file_path,header=0, sheet_name=None):
    url = f"{NEXTCLOUD_URL}{file_path}"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            df = pd.read_excel(io.BytesIO(response.content), header=header, sheet_name=sheet_name,engine='openpyxl')
            return df
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to Load the master: {e}")
        return []

biosourcekey = get_excel_file_as_dataframe('/DOCUMENTATION/naming_key.xlsx',sheet_name='table1')
instrumentkey = get_excel_file_as_dataframe('/DOCUMENTATION/naming_key.xlsx',sheet_name='table2')
researcherkey = get_excel_file_as_dataframe('/DOCUMENTATION/naming_key.xlsx',sheet_name='table3')

# Here the page begins
st.title("AC/BC 🦦")
st.caption("Atlantic Canada Biochar Project")
st.caption("Made by Brian Espinosa Acosta")

st.header("About US!",divider='green')

st.write('''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
   ''')

st.header("Data Management Tips",divider = "green")
st.write('''### Sample naming:''')
st.caption('Follow this steps to name your sample')
st.write('''Create a "unique sample name" every time that you produce or process a feedstock or
biochar and may result in a new material with different adsorption capacity. Follow this even if you
not intend to measure the capacity. ''')

st.write('''
Template: 
    
    ACBCX_XXX####_XX###
''')
st.write('''Breakdown:  
* **ACBCX**: (ACBC) Atlantic Canada Biochar project + (X) PI last name initial.  
:red[Note: the researcher does not need to write this. The data manager will fill out this part automatically.]  
* **XXX####**: Three letter researcher acronym + four number sample code.  
:red[Note: Important linkage to the instrument output datafile name.]  
* **XX###**: Two letter generic feedstock + temperature in Celsius  
* **"_"**: Splitter underscore. :red[DO NOT LEAVE SPACES]
''')
st.write('''Example:  
Let's say that researcher **Brian** produced a new sample that is its **second** ever. The sample will likely have a different capacity.
The sample feedstock source is **oak (hardwood)** and it was created using fast pyrolisis at **400°C**. Brian works under the supervision of PI
Dr. **Poduska**.  
Use the Sample Naming Keys 👇 to build the sample name.''')
with st.expander("See Naming Keys"):
    ckey1,ckey2 = st.columns((1,1))
    with ckey1:
        st.dataframe(biosourcekey,hide_index=True, use_container_width=True)
    with ckey2:
        st.dataframe(instrumentkey,hide_index=True, use_container_width=True)
        st.dataframe(researcherkey,hide_index=True, use_container_width=True)
st.write('''Brian should name his sample: **BEA0002_HW400**  
Then the data manager will add the project code and PI initial: **ACBCP**  
The full sample reference code will be: **ACBCP_BEA0002_HW400**''')


st.write('''
### Instrument file naming:  
''')
st.write('''
Template: 
    
    ACBCX_XXX####_XXX_YYYYMMDD_##.dat

Breakdown:  
* **ACBCX_XXX####**:  Same as for the sample name.  
:red[Note: Remember ACBCX will be filled by the software]  
* **XXX**: Three-letter instrument acronym.  
* **YYYYMMDD**: Date ISO standard.  
* **##**: Run number
* **.dat**: file format preferred :red[.csv] or :red[.dpt]  
* **"_"**: Splitter underscore. :red[DO NOT LEAVE SPACES]
	
Example:  
**ABCDP_BEA0002_ATR_20250122_01.csv**  
Breakdown:
* **ABCDP_BEA0002**: As explained before
* **ATR**: Attenuated total reflectance
* **20250122**: Recorded on Jan, 22nd 2025
* **01**: Run number 1
''')

st.write('''
### Read related documentation 👇
''')

url1 = 'https://nextcloud.computecanada.ca/index.php/s/pwrdiEYzLXdKDbs'
url2 = 'https://nextcloud.computecanada.ca/index.php/s/k9tZ3A96NdExC24'
# Create the button
col1,col2 = st.columns(2)
with col1:
    st.markdown(f"""
        <a href="{url1}" target="_blank">
            <button style="background-color:Green; color:white; padding:10px 20px;
             border:none; border-radius:5px;
             cursor:pointer; font-size:16px;
            font-weight:bold;">
                Biochar DMP 📄
            </button>
        </a>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <a href="{url2}" target="_blank">
            <button style="background-color:Green; color:white; padding:10px 20px;
             border:none; border-radius:5px;
             cursor:pointer; font-size:16px;
            font-weight:bold;">
                Biochar Excerpt 📄
            </button>
        </a>
    """, unsafe_allow_html=True)

st.write('')
st.write('')

st.header("Learn About Biochars",divider='green')

url3 = 'https://biochar-international.org/'
url4 = 'https://biochar.ucdavis.edu/'
url5 = 'https://biochar-us.org/index.php/'

for i in [url3,url4,url5]:
    st.write(f'''* {i}''')