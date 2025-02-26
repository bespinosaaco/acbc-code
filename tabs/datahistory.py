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



