import os
import subprocess
import platform

def git_clone(url, path, depth=1, branch=None, commit=None, hide_terminal=True):
    """
    Clone a Git repository from the given URL with optional depth, branch, or commit.
    
    Args:
        url (str): The URL of the Git repository.
        path (str): Path to where repository will be cloned
        depth (int, optional, default = 1): The depth of the clone (number of commits to include).
        branch (str, optional, default = None): The branch to clone (ignored if commit is specified).
        commit (str, optional, default = None): The commit hash or reference to clone (takes precedence over branch).
        hide_terminal (boolean, optional, default = True): Run while hiding terminal
    
    Returns:
        bool: True if the clone was successful, False otherwise.
    """
    
    if not os.path.isabs(path):  # Check if path is relative
        path = os.path.join(os.getcwd(), path)  # Prepend current working directory
    if not os.path.exists(path):
        os.makedirs(path)
    
    command = ['git', 'clone']
    
    if depth is not None:
        command.extend(['--depth', str(depth)])
    
    if commit is not None:
        command.extend(['--single-branch', '--tags'])
        command.append(url)
        subprocess.run(command, check=True)
        
        # Change to the cloned repository directory
        repo_name = url.split('/')[-1].split('.git')[0]
        subprocess.run(['cd', repo_name], shell=True)
        
        # Fetch the specific commit
        fetch_command = ['git', 'fetch', '--depth=1', 'origin', commit]
        subprocess.run(fetch_command, check=True)
        
        # Checkout the specific commit
        checkout_command = ['git', 'checkout', commit]
        subprocess.run(checkout_command, check=True)
        
        return True
    
    if branch is not None and commit is None:
        command.extend(['--branch', branch])
    
    command.extend([url, path])
    
    try:
        if platform.system() == 'Windows' and hide_terminal:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(command, check=True, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        elif platform.system() == 'Darwin' and hide_terminal:
            script = f'tell application "Terminal" to do script "{subprocess.list2cmdline(command)}"'
            subprocess.run(['osascript', '-e', script], check=True)
        else:
            # For other platforms, fall back to the default behavior (visible terminal)
            subprocess.run(command, check=True)    
        return True
    except subprocess.CalledProcessError as e:
        # Handle the error
        stderr_output = e.stderr.decode("utf-8")  # Decode the stderr output
        print("Error occurred:")
        print(stderr_output)
        return False
