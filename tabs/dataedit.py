import streamlit as st

st.warning("Page under work ⚒️!")
st.caption("Scroll to the bottom of the table to add row")
if 'master' in st.session_state:
    master = st.session_state['master']
else:
    st.error("Master Inventory hasn't load")

st.data_editor(master,hide_index=True,num_rows="dynamic")