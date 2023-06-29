#####################################################################################################
# Defines ###########################################################################################
#####################################################################################################

# Define named tuple types
from collections import namedtuple

clone_request = namedtuple("clone_request", ["url", "branch", "commit"])
clone_info = namedtuple("clone_info", ["url", "branch", "commit", "clone_attempted", "clone_status", "clone_path"])

# Define enums
from enum import Enum, auto

class VersionAction(Enum):
    USE_TARGET_IF_ARGUMENT_ELSE_NEWEST = auto() #Default
    ALL_NEWEST = auto()
    ALWAYS_USE_TARGET = auto()

#####################################################################################################
# Core ##############################################################################################
#####################################################################################################
import sys
import os

import App_MultiClone.globals

from App_MultiClone.sub.clone_url import git_clone_url
from App_MultiClone.sub.clone_url import clone_result
from App_MultiClone.sub.post_clone_handler import repository_action

# Main
def main(clone_request_list, path=None, version_action=VersionAction.USE_TARGET_IF_ARGUMENT_ELSE_NEWEST, force=True, depth=1):
    """
    Main function to perform the cloning process. When all provided elements have been cloned each repository will be searched (in order) for content of ".dependencies".
    ".dependencies". should be formatted as the clone_request_list using linefeed instead of ";".
    ".dependencies" will be cloned while new dependencies are found.

    Args:
        clone_request_list (list): List of clone_request objects. Use space separated branch= or commit= to specify specific target version.
        path (str, optional, default = os.getcwd()): The absolute clone target path.
        version_action (VersionAction, optional): Version action to perform. Default is USE_TARGET_IF_ARGUMENT_ELSE_NEWEST.
        force (bool, optional): Whether to force removal of existing repositories. Default is True.
        depth (int, optional): The depth of the clone (number of commits to include). Default is 1.

    Returns:
        list: List of boolean values indicating the success of each cloning operation.
    """

    # Print config
    print("")
    print("App_MultiClone (version 0.0.1.0)")
    print("")
    print("Config:")
    print(f"  Path: {path}")
    print(f"  Version action: {version_action.name}")
    print(f"  Force: {force}")
    print(f"  Depth: {depth}")
    print("")

    # Create clone folders
    main_path = os.path.join(path, "main")
    if not os.path.exists(main_path):
        os.makedirs(main_path)
    sub_path = os.path.join(path, "sub")
    if not os.path.exists(sub_path):
        os.makedirs(sub_path)
    print("Create target folders:")
    print(f"  Main: {main_path}")
    print(f"  Sub: {sub_path}")
    print("")

    # Parse clone_request_list into a clone_info_list
    clone_info_list = []
    clone_url_list = []
    for request in clone_request_list:
        clone_info_list.append(clone_request_to_info_element(request))    
        clone_url_list.append(request.url)
    
    # Pre-clone handling of VersionAction.ALL_NEWEST
    if version_action == VersionAction.ALL_NEWEST:
        for i, info in enumerate(clone_info_list):
            if info.branch and info.branch.startswith("tags/"):  # Tag disregarded
                clone_info_list[i] = info._replace(branch=None)
            if info.commit:  # Commit disregarded
                clone_info_list[i] = info._replace(commit=None)

    # Requested clone
    print("Clone requested repositories:")
    clone_info_list = execute_clone(clone_info_list, main_path=main_path, version_action=version_action, force=force, depth=depth)
    
    # Build boolean status array
    status_array = []
    clone_attempted_array = []
    for info in clone_info_list:
        clone_attempted_array.append(info.clone_attempted)
        if info.clone_attempted:
            status_array.append(info.clone_status)

    # Initial result evaluation
    if status_array and all(status_array):
        print("Requested clone operations successful, check for dependencies")
    elif status_array and any(status_array):
        print("Some clone operations failed, check for dependencies")
    elif status_array:
        print("All clone operations failed - Abort")
        sys.exit(1)
    else:
        print("No clone operations performed - Abort")
        sys.exit(1)
    print("")
    
    # Clone dependencies
    if not all(clone_attempted_array):
        print("Clone dependencies:")
        all_done = False
        while not all_done:
            clone_info_list = execute_clone(clone_info_list, main_path=main_path, version_action=version_action, force=force, depth=depth)
            clone_attempted_array = []
            for info in clone_info_list:
                clone_attempted_array.append(info.clone_attempted)
            all_done = all(clone_attempted_array)

        # Result evaluation
        status_array = []
        for info in clone_info_list:
            status_array.append(info.clone_status)
        if status_array and all(status_array):
            print("All dependency clone operations successful")
        elif status_array and any(status_array):
            print("Some clone operations failed")
        print("")

    # Post clone action handling
    path_array = []
    for info in clone_info_list:
        if info.clone_status:
            path_array.append(info.clone_path)
    repository_action(paths=path_array)

        
    result = all(status_array)
    return result

#####################################################################################################
# Functions #########################################################################################
#####################################################################################################

def string_to_clone_elements(string, delimiter=";", version_action=None):
    """
    Parse a string into an array of clone_info elements.

    Args:
        string (str): string to parse into clone_request_list.
        delimiter (str, optional, default = ";"): Delimiter used to split clone_info elements.
        version_action (VersionAction, optional, default=None): Version action use on parsed string. Filtering disabled if None.

    Returns:
        clone_request_list (clone_info array) : List of clone_info elements.
    """
    
    get_newest = ( version_action == VersionAction.ALL_NEWEST or version_action == VersionAction.USE_TARGET_IF_ARGUMENT_ELSE_NEWEST )
    
    clone_request_list = []
    url_list = string.split(delimiter)
    
    for url in url_list:
        url_parts = url.split()
        url_info = clone_request(url=url_parts[0], branch=None, commit=None)
        for part in url_parts[1:]:
            if part.startswith("branch="):
                branch_name = part[len("branch="):]
                is_branch = not branch_name.startswith("tags/")
                if is_branch:  # never skip branch
                    url_info = url_info._replace(branch=branch_name) 
                elif not get_newest:  # skip tag if get newest
                    url_info = url_info._replace(branch=branch_name)
            elif part.startswith("commit=") and not get_newest:  # skip commit getting newest
                url_info = url_info._replace(commit=part[len("commit="):])
        clone_request_list.append(url_info)
        
    return clone_request_list

def clone_request_to_info_element(request):
    """
    Converts a clone request to an info element by adding the missing parts with their default values.

    Args:
        request

    Returns:
        clone_info
    """
    
    clone_info_element = clone_info(url=request.url, branch=request.branch, commit=request.commit, clone_attempted=False, clone_status=False, clone_path=None)
    return clone_info_element

def execute_clone(clone_info_list, main_path, version_action, force=False, depth=1):
    """
    Clone .

    Args:
        clone_info_list (clone_info array) : List of clone_info elements to clone.
        main_path (str): Path to the clone target.
        version_action (VersionAction): Version action to perform. Only in use when getting dependencies.
        force (bool, optional, default=False): Whether to force removal of existing repositories. Default is True.
        depth (int, optional, default=1): The depth of the clone (number of commits to include). Default is 1.

    Returns:
        clone_info_list (clone_info array) : List of clone_info elements.
    """

    # Build url array
    url_array = []
    for info in clone_info_list:
        url_array.append(info.url)
    
    
    # Clone
    clone_info_list_addition = []
    for i, info in enumerate(clone_info_list):
        if not info.clone_attempted:
            info = info._replace(clone_attempted=True)
            clone_result = git_clone_url(info.url, path=main_path, force=force, depth=depth, branch=info.branch, commit=info.commit)
            clone_status = clone_result.status
            clone_path = clone_result.path
            clone_dependencies_path = os.path.join(clone_path, ".dependencies")
            info = info._replace(clone_status=clone_status, clone_path=clone_path)
            clone_info_list[i] = info
            if clone_status and os.path.exists(clone_dependencies_path):
                # Load dependencies
                with open(clone_dependencies_path, 'r') as file:
                    dependencies_content = file.read()
                dependency_clone_request_list = string_to_clone_elements(dependencies_content, delimiter="\n", version_action=version_action)
                for request in dependency_clone_request_list:
                    if request.url not in url_array:
                        clone_info_list_addition.append(clone_request_to_info_element(request))
    
    # Add found dependencies to return value
    clone_info_list.extend(clone_info_list_addition)
    
    return clone_info_list

#####################################################################################################
# CLI ###############################################################################################
#####################################################################################################

# Handle CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("")
        print("Usage: python Main.py <url_list> [--path <value>] [--force <value>] [--depth <value>]")
        print("  <url_list>: Semicolon separated list of urls to clone. Specific versions can be acquired by space separated addition of:")
        print("    branch=<branc name>: name of branch to clone")
        print("    commit=<commit>: ID of specific commit to clone (disregards branch if present, however is disregarded itself on use of ALL_NEWEST)")
        print("  --path: Absolute path to roo clone folder (optional, default: os.getcwd())")
        print("  --version-action: Specifies how to handle repository versioning. Accepted values string or number:")
        print("    1: USE_TARGET_IF_ARGUMENT_ELSE_NEWEST")
        print("    2: ALL_NEWEST")
        print("    3: ALWAYS_USE_TARGET")
        print("  --force: Whether to force clone (optional, default: True)")
        print("  --depth: Clone depth (optional, default: 1)")
        print("")
        sys.exit(1)
    else:

        # Sanity check clone_info - url_list
        url_list = sys.argv[1].split(";")
        if not url_list:
            print("No URLs provided. Exiting...")
            sys.exit(1)

        # Parse url list and build clone_request_list
        clone_request_list = string_to_clone_elements(sys.argv[1], ";")

        # Get path argument
        if "--path" in sys.argv:
            path_index = sys.argv.index("--path")
            if path_index + 1 < len(sys.argv):
                path = sys.argv[path_index + 1]
            else:
                path = None
        else:
            path = None
            
        # Get version-action argument
        if "--version-action" in sys.argv:
            action_index = sys.argv.index("--version-action")
            if action_index + 1 < len(sys.argv):
                action_value = sys.argv[action_index + 1]
                try:
                    version_action = int(action_value)  # Try parsing as an integer
                except ValueError:
                    version_action = action_value  # Treat as a string
            else:
                version_action = VersionAction.USE_TARGET_IF_ARGUMENT_ELSE_NEWEST  # Default value
        else:
            version_action = VersionAction.USE_TARGET_IF_ARGUMENT_ELSE_NEWEST  # Default value

        # Get force argument
        if "--force" in sys.argv:
            force_index = sys.argv.index("--force")
            if force_index + 1 < len(sys.argv):
                force = bool(sys.argv[force_index + 1])
            else:
                force = True
        else:
            force = True

        # Get depth argument
        if "--depth" in sys.argv:
            depth_index = sys.argv.index("--depth")
            if depth_index + 1 < len(sys.argv):
                depth = int(sys.argv[depth_index + 1])
            else:
                depth = 1
        else:
            depth = 1

        # Call main
        main(clone_request_list, path=path, version_action=version_action, force=force, depth=depth)
