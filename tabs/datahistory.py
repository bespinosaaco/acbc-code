import pandas as pd
from github import Github, GithubException
import streamlit as st
from datetime import date, datetime
import io

# GitHub configuration
GITHUB_TOKEN = st.secrets['GitHub']['token']
USERNAME = st.secrets['GitHub']['username']
REPO_NAME = st.secrets['GitHub']['repo']
FILE_PATH_ON_GITHUB = 'datalog/master.csv'
date = datetime.today().strftime('%Y-%m-%d')

# GitHub operations
def upload_to_github1(df, file_path_on_github, name, note, date):
    g = Github(GITHUB_TOKEN)
    repo = g.get_user(USERNAME).get_repo(REPO_NAME)

    # Convert DataFrame to CSV string for comparison
    new_content = df.to_csv(index=False)

    try:
        # Check if the CSV already exists in the repo
        contents = repo.get_contents(file_path_on_github)
        existing_content = contents.decoded_content.decode('utf-8')

        if new_content == existing_content:
            st.warning(
                f"The CSV in the repository is identical to the one being pushed. No update needed.")
        else:
            # Update or create the file
            repo.update_file(
                path=file_path_on_github,
                message=f"{name} Updated CSV file on {date}. Note: {note}",
                content=new_content,
                sha=contents.sha
            )
            st.success('Added to repository')
            st.write('Commit message:')
            st.write(f"{name} Updated CSV file on {date}. Note: {note}")

    except GithubException as e:
        if e.status == 404:  # File not found
            # If file doesn't exist, create it
            repo.create_file(
                path=file_path_on_github,
                message=f"{name} Created new CSV file on {date}. Note: {note}",
                content=new_content
            )
            st.success(f"New file created at {file_path_on_github}")
        else:
            st.error(f"An error occurred while checking or updating the file: {e}")

### Page starts here ###
with st.popover("Log In"):
    st.markdown("Administrative credentials")
    name = st.text_input("What's your name?",placeholder='John')

if name in ['Brian','Kris','Jack']:

    st.write(date)

    st.write('''
            # Version control 😶‍🌫️ 
            Submit current inventory to version control
    ''')

    if 'master' in st.session_state:
        st.write(st.session_state['master'])
    else:
        st.error('Master not loaded')

    with st.form('datalog'):
        name = st.text_input('Name', max_chars=10)
        note = st.text_area("Add a note for the log history", value='None', max_chars=140)
        submitted = st.form_submit_button('Submit to version control')

        if submitted:
            if name and 'master' in st.session_state:
                upload_to_github1(st.session_state['master'], FILE_PATH_ON_GITHUB,name,note,date)

            else:
                st.error('Add your name')
else:
    st.warning("Get access")