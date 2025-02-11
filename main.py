import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
# Web appearance configuration
st.set_page_config(page_title="AC/BC Visualize", page_icon='🧪',
                   layout="wide",
                   menu_items={
                       'Get Help': 'mailto:bespinosaaco@mun.ca',
                   }
                   )
st.logo('assets/logo.png',
        link="https://www.ofi.ca/news/ocean-frontier-institute-moves-into-new-space-at-memorial-university",
        size="large")  # Add a link here to TCA

# Load config at the start of the app
with open('.streamlit/config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize session state for login attempts
if "login_attempts" not in st.session_state:
    st.session_state['login_attempts'] = 0

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

def handle_error(e, message):
    if isinstance(e, (LoginError, RegisterError, ResetError, UpdateError)):
        st.error(f"{message}: {str(e)}")
    else:
        st.error(f"An error occurred: {str(e)}")

def handle_login_error():
    if st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
        st.session_state["login_attempts"] += 1
        if st.session_state["login_attempts"] >= 3:
            handle_forgotten_username()
            handle_forgotten_password()
            save_config()

def handle_forgotten_username():
    try:
        username, email = authenticator.forgot_username()
        if username:
            st.success('Username to be sent securely')
            st.info("Not implemented yet!")
        elif username is False:
            st.error('Email not found')
    except Exception as e:
        handle_error(e, "Error in retrieving username")

def handle_forgotten_password():
    try:
        username_of_forgotten_password, \
            email_of_forgotten_password, \
            new_random_password = authenticator.forgot_password()
        if username_of_forgotten_password:
            st.success('New password to be sent securely')
            st.info("Showing the password until getting secure way to share")
            st.info(new_random_password)
            # The developer should securely transfer the new password to the user.
        elif username_of_forgotten_password == False:
            st.error('Username not found')
    except Exception as e:
        handle_error(e, "Error in recovering password")

def save_config():
    with open('.streamlit/config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)

def reset_password():
    try:
        if authenticator.reset_password(st.session_state['username']):
            st.success('Password modified successfully')
            save_config()
    except Exception as e:
        handle_error(e, "Password reset failed")

def update_details():
    try:
        if authenticator.update_user_details(st.session_state['username']):
            st.success('Entries updated successfully')
            save_config()
    except Exception as e:
        st.error(e)

def account_setting_page():
    """
    Create the account setting page
    It has to be in the main.py to avoid key issues
    """
    st.title('Account Settings')
    st.write('---')
    st.write(f'''Hi **{st.session_state["name"]}**, update your credentials 👇''')
    if st.session_state["authentication_status"] is not None:
        reset_password()
        update_details()

def app_ini():
    """Initiate the app navigation"""

    pages = {
        "Inventory": [
            st.Page("tabs/dashboard.py", title="Dashboard",default=True),
            st.Page("tabs/dataedit.py", title="Data Edit"),
        ],
        "Data History" : [
            st.Page("tabs/datahistory.py", title="Update"),
        ],
        "About": [
            st.Page("tabs/docs.py", title="Info"),
            st.Page(account_setting_page,title="Account Settings"),
        ],
    }

    pg = st.navigation(pages)
    pg.run()


# Login structure
if not st.session_state["authentication_status"]:
    st.title("Welcome to AC/BC 🦦")
    login_tab,outh2_tab, regist_tab = st.tabs(["Login","Login with", "Sign Up"])
    with login_tab:
        try:
            authenticator.login(single_session=True)
            save_config()
            handle_login_error()
        except Exception as e:
            handle_error(e, "Login failed")

    with outh2_tab:
        st.info("Still working on this ⚒️")
        ggle_col,msft_col = st.columns(2)
        with ggle_col:
            st.warning("The google button goes here")
        with msft_col:
            st.warning("The microsoft button goes here")
    with regist_tab:
        try:
            email, username, name = authenticator.register_user(clear_on_submit=True)
            if email in config['pre-authorized2']['emails']:
                st.success('User registered successfully')
                st.success('Use the login tab 👈')
                save_config()  # Save config only if registration was successful and email is in pre-authorized2
            elif email == None:
                st.info("Fill out the registration form")
            else:
                st.error("Your email is not pre-authorized contact admin")

        except RegisterError as e:
            handle_error(e, "Registration failed")

    with st.sidebar:
        st.warning("You have to be logged in")

# When logged in
if st.session_state["authentication_status"]:
    st.session_state['login_attempts'] = 0 # Re-initiate the login attempts
    with st.sidebar:
        authenticator.logout()
        save_config()

    ## The function for the app
    app_ini()
