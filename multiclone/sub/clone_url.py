import os
import subprocess

from collections import namedtuple

from multiclone.sub.git.clone import git_clone

# Define named tuple type
clone_result = namedtuple("clone_result", ["path", "status"])

def git_clone_url(url, path=None, force=True, depth=1, branch=None, commit=None):
    """
    Clone a Git repository from the given URL with optional depth, branch, or commit.
    
    Args:
        url (str): The URL of the Git repository.
        path (str, optional, default = os.getcwd()): The absolute clone target path.
        force (boolean, optional, default = True): If repo is already cloned it will be deleted before cloning!
        depth (int, optional, default = 1): The depth of the clone (number of commits to include).
        branch (str, optional, default = None): The branch to clone (ignored if commit is specified).
        commit (str, optional, default = None): The commit hash or reference to clone (takes precedence over branch).
    
    Returns:
        clone_result:
          path (str): Path to cloned repository.
          status (boolean): True if the clone was successful, False otherwise.
    """
    # Print header
    print(f"  Clone {url}")
    
    # Sanity check for a valid URL
    if not url.startswith('http'):
        print(f"    Invalid URL: {url}")
        return clone_result(path="", status=False)

    # Handle path parameter
    if path is None:
        path = os.getcwd()

    # Acquire repo details
    repo_name = extract_repo_name(url)
    repo_path = os.path.join(path, repo_name)  # Build repo path 

    # Force handling
    if os.path.exists(repo_path) and force:
        try:
            # Removal using rmdir (note: shutil.rmtree does not have required access)
            command = ["rmdir", repo_path, "/s", "/q"]
            subprocess.run(command, shell=True)
            print(f"    Forced removal of: {repo_name}")
        except subprocess.CalledProcessError as e:
            print(f"    Forced removal failure for: {repo_name}")
            return clone_result(path=repo_path, status=False)
    elif os.path.exists(repo_path) and not force:
        print(f"    Repository already exists, clone skipped: {repo_name}")
        return clone_result(path=repo_path, status=True)

    # Call clone action
    success = git_clone(url, repo_path, depth, branch, commit)

    if success:
        print(f"    Successfully cloned repository: {repo_name}")
    else:
        print(f"    Failed to clone repository: {repo_name}")
    return clone_result(path=repo_path, status=success)

def extract_repo_name(url):
    """
    Extract repository name from provided url. If the name contains ".." everything before ".." will be removed.
    
    Args:
        url (str): The URL of the Git repository.
        
    Returns:
        string: The name of the repository with anything before ".." removed.
    """
    url_components = url.split("/")
    if ".." in url_components[-1]:
        return url_components[-1].split("..", 1)[1]
    else:
        return url_components[-1]
