import pandas as pd
from github import Github
import streamlit as st

# GitHub configuration
GITHUB_TOKEN = st.secrets['GitHub']['token']
USERNAME = st.secrets['GitHub']['username']
REPO_NAME = st.secrets['GitHub']['repo']
FILE_PATH_ON_GITHUB = 'datalog/master.csv'

name = 'Brian'
# GitHub operations
def upload_to_github(df, file_path_on_github):
    g = Github(GITHUB_TOKEN)
    repo = g.get_user(USERNAME).get_repo(REPO_NAME)

    # Convert DataFrame to CSV string
    content = df.to_csv(index=False)  # index=False to exclude row indices in CSV

    # Check if file exists, if not, create it
    try:
        contents = repo.get_contents(file_path_on_github)
        repo.update_file(
            path=file_path_on_github,
            message=f"Updated CSV file by {name}",
            content=content,
            sha=contents.sha
        )
    except:
        repo.create_file(
            path=file_path_on_github,
            message="Add CSV file",
            content=content
        )
    print(f"File uploaded to {file_path_on_github}")


### Page starts here ###

if 'master' in st.session_state:
    st.write(st.session_state['master'])
else:
    st.error('Master not loaded')


# upload_to_github(df, FILE_PATH_ON_GITHUB)