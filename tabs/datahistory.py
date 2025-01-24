import pandas as pd
from github import Github
import streamlit as st
from datetime import date, datetime

# GitHub configuration
GITHUB_TOKEN = st.secrets['GitHub']['token']
USERNAME = st.secrets['GitHub']['username']
REPO_NAME = st.secrets['GitHub']['repo']
FILE_PATH_ON_GITHUB = 'datalog/master.csv'
date = datetime.today().strftime('%Y-%m-%d')
st.write(date)
# GitHub operations
def upload_to_github(df, file_path_on_github,name,note,date):
    g = Github(GITHUB_TOKEN)
    repo = g.get_user(USERNAME).get_repo(REPO_NAME)

    # Convert DataFrame to CSV string
    content = df.to_csv(index=False)  # index=False to exclude row indices in CSV

    # Check if file exists, if not, create it
    try:
        contents = repo.get_contents(file_path_on_github)
        repo.update_file(
            path=file_path_on_github,
            message=f"{name} Updated CSV file on {date}. Note: {note}",
            content=content,
            sha=contents.sha
        )
    except:
        repo.create_file(
            path=file_path_on_github,
            message=f"{name} Updated CSV file on {date}. Note: {note}",
            content=content
        )
    print(f"File uploaded to {file_path_on_github}")


### Page starts here ###

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
            upload_to_github(st.session_state['master'], FILE_PATH_ON_GITHUB,name,note,date)
            st.success('Added to repository')
            st.write('Commit message:')
            st.write(f"{name} Updated CSV file on {date}. Note: {note}")
        else:
            st.error('Add your name')
