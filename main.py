import streamlit as st
import hmac

st.set_page_config(page_title="AC/BC Visualize",page_icon = '🧪',layout="wide")
st.logo('assets/logo.png',link = "https://www.ofi.ca/news/ocean-frontier-institute-moves-into-new-space-at-memorial-university",size="large")  #Add a link here to TCA

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["nextcloud"]["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.title("Welcome to AC/BC 🦦")
    st.write(''' ### Insert group's password to access''')
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

pages = {
    "Inventory": [
        st.Page("tabs/dashboard.py", title="Dashboard"),
        st.Page("tabs/dataedit.py", title="Data Edit"),
    ],
    "About": [
        st.Page("tabs/docs.py", title="Info"),
    ],
}

pg = st.navigation(pages)
pg.run()