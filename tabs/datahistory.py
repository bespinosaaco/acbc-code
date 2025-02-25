import streamlit as st
import pandas as pd
import os
import subprocess
from datetime import datetime

date = datetime.today().strftime('%Y-%m-%d')
directory = 'datalog'

# Helper functions
def is_repo_initialized():
    return os.path.exists(os.path.join(directory, '.git'))

def is_master_created():
    return os.path.exists(os.path.join(directory, 'master.csv'))

@st.cache_data
def configure_git_committer(committer_name, committer_email):
    if not is_repo_initialized():
        return
    subprocess.run(['git', 'config', 'user.name', committer_name], cwd=directory, check=True)
    subprocess.run(['git', 'config', 'user.email', committer_email], cwd=directory, check=True)
    return committer_name

def init_repo():
    if not os.path.exists(directory):
        os.makedirs(directory)
    subprocess.run(['git', 'init'], cwd=directory, check=True)

def commit(data, commit_message,directory):
    # Save the DataFrame to master.csv
    csv_path = os.path.join(directory, 'master.csv')
    data.to_csv(csv_path, index=False)

    # Stage the file
    subprocess.run(['git', 'add', 'master.csv'], cwd=directory, check=True)

    # Attempt to commit, capturing output to diagnose failures
    result = subprocess.run(
        ['git', 'commit', '-m', commit_message],
        cwd=directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True  # Returns strings instead of bytes
    )

    # Check the result
    if result.returncode != 0:
        error_output = result.stderr.lower()
        if "nothing to commit" in error_output or "nothing to commit" in result.stdout.lower():
            st.info("No changes to commit.")
        else:
            raise subprocess.CalledProcessError(
                result.returncode, result.args, output=result.stdout, stderr=result.stderr
            )
    else:
        st.success("DataFrame committed successfully.")

def show_diff():
    try:
        commit_count = int(subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            cwd=directory,
            stdout=subprocess.PIPE,
            universal_newlines=True
        ).stdout.strip())
        if commit_count < 2:
            return "Not enough commits to show differences."
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', '--', 'master.csv'],
            cwd=directory,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        return result.stdout or "No differences found."
    except subprocess.CalledProcessError as e:
        return f"Error running Git diff: {e}"

# Main logic
if not is_repo_initialized():
    init_repo()
    st.success("Git repository initialized in 'datalog' directory.")
else:
    st.info("Git repository is active.")

if all(key in st.session_state for key in ['name', 'email', 'roles']):
    committer_name = st.session_state['name']
    committer_email = st.session_state['email']
    if "Administrator" in st.session_state["roles"]:
        st.write(date)
        st.write('''
            # Version control 😶‍🌫️
            Submit current inventory to version control
        ''')

        # Load DataFrame if not in session state
        if 'master' not in st.session_state and is_master_created():
            st.session_state['master'] = pd.read_csv(os.path.join(directory, 'master.csv'))
        if 'master' in st.session_state:
            master = st.session_state['master']
            st.write(master)
        else:
            st.error('Master not loaded')

        commit_message = st.text_input(label="Add the commit message", max_chars=40,
                                       placeholder="Short commit message max 40 chars")

        st.write(f"**{committer_name}** will commit:  \n**{commit_message}**  \nEffective: **{date}**")

        if st.button("Commit to datalog"):
            if not commit_message:
                st.error("Please provide a commit message.")
            else:
                configure_git_committer(committer_name, committer_email)
                commit(master, commit_message,directory)

        if st.button("Show Differences"):
            diff_output = show_diff()
            st.code(diff_output, language="diff")
    else:
        st.warning("Talk to an administrator to get access")
else:
    st.error("Session state missing required keys: 'name', 'email', or 'roles'.")

# from github import Github, GithubException
# import io
# GitHub configuration
# GITHUB_TOKEN = st.secrets['GitHub']['token']
# USERNAME = st.secrets['GitHub']['username']
# REPO_NAME = st.secrets['GitHub']['repo']
# FILE_PATH_ON_GITHUB = 'datalog/master.csv'
#
# # GitHub operations
# def upload_to_github1(df, file_path_on_github, name, note, date):
#     g = Github(GITHUB_TOKEN)
#     repo = g.get_user(USERNAME).get_repo(REPO_NAME)
#
#     # Convert DataFrame to CSV string for comparison
#     new_content = df.to_csv(index=False)
#
#     try:
#         # Check if the CSV already exists in the repo
#         contents = repo.get_contents(file_path_on_github)
#         existing_content = contents.decoded_content.decode('utf-8')
#
#         if new_content == existing_content:
#             st.warning(
#                 f"The CSV in the repository is identical to the one being pushed. No update needed.")
#         else:
#             # Update or create the file
#             repo.update_file(
#                 path=file_path_on_github,
#                 message=f"{name} Updated CSV file on {date}. Note: {note}",
#                 content=new_content,
#                 sha=contents.sha
#             )
#             st.success('Added to repository')
#             st.write('Commit message:')
#             st.write(f"{name} Updated CSV file on {date}. Note: {note}")
#
#     except GithubException as e:
#         if e.status == 404:  # File not found
#             # If file doesn't exist, create it
#             repo.create_file(
#                 path=file_path_on_github,
#                 message=f"{name} Created new CSV file on {date}. Note: {note}",
#                 content=new_content
#             )
#             st.success(f"New file created at {file_path_on_github}")
#         else:
#             st.error(f"An error occurred while checking or updating the file: {e}")
#
#
#     with st.form('datalog'):
#         name = st.text_input('Name', max_chars=10)
#         note = st.text_area("Add a note for the log history", value='None', max_chars=140)
#         submitted = st.form_submit_button('Submit to version control')
#
#         if submitted:
#             if name and 'master' in st.session_state:
#                 upload_to_github1(st.session_state['master'], FILE_PATH_ON_GITHUB,name,note,date)
#
#             else:
#                 st.error('Add your name')
#

