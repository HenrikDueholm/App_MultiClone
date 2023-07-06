#####################################################################################################
# Import ############################################################################################
#####################################################################################################

# System
import sys
import os

from collections import namedtuple
from enum import Enum, auto

# Non-system
from multiclone.sub.globals import globals_object

from multiclone.sub.clone_url import git_clone_url
from multiclone.sub.post_clone_handler import post_clone_action_handler
from multiclone.sub.path import build_clone_dependencies_path

#####################################################################################################
# Define ############################################################################################
#####################################################################################################

# Define named tuple types
clone_request = namedtuple("clone_request", ["url", "branch", "commit"])
clone_info = namedtuple("clone_info", ["url", "branch", "commit", "clone_attempted", "clone_status", "clone_path"])

# Define enums
class VersionAction(Enum):
    USE_TARGET_IF_ARGUMENT_ELSE_NEWEST = auto()  # Default
    ALL_NEWEST = auto()
    ALWAYS_USE_TARGET = auto()

#####################################################################################################
# main ##############################################################################################
#####################################################################################################

def main(clone_request_list, path=None, version_action=VersionAction.USE_TARGET_IF_ARGUMENT_ELSE_NEWEST,
         force=True, depth=1):
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
    print("MultiClone (version 0.1.1)")
    print("")
    print("Config:")
    print(f"  Path: {path}")
    print(f"  Version action: {version_action.name}")
    print(f"  Force: {force}")
    print(f"  Depth: {depth}")
    print("")
    print("Details:")
    print(f"  Working directory: {os.getcwd()}")
    print("")

    # Create clone folders
    path_main = os.path.join(path, "main")
    if not os.path.exists(path_main):
        os.makedirs(path_main)
    path_source = os.path.join(path, "source")
    if not os.path.exists(path_source):
        os.makedirs(path_source)
    print("Create target folders:")
    print(f"  Main: {path_main}")
    print(f"  Source: {path_source}")
    print("")

    # Populate global
    globals_object.path_main = path_main
    globals_object.path_source = path_source
    globals_object.force = force

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
    clone_info_list = execute_clone(clone_info_list, path_source=path_source, version_action=version_action,
                                    force=force, depth=depth)
    
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
    clone_action_result = True
    if not all(clone_attempted_array):
        print("Clone dependencies:")
        all_done = False
        while not all_done:
            clone_info_list = execute_clone(clone_info_list, path_source=path_source, version_action=version_action,
                                            force=force, depth=depth)
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
        clone_action_result = all(status_array)

    # Post clone action handling
    path_array = []
    for info in clone_info_list:
        if info.clone_status:
            path_array.append(info.clone_path)

    action_result = post_clone_action_handler(path_array, plugin_folders=None)  # ToDo:
    # Add plugin_folders config (external config?)

    return clone_action_result and action_result

#####################################################################################################
# Functions #########################################################################################
#####################################################################################################

def string_to_clone_elements(string, delimiter=";", version_action=None):
    """
    Parse a string into an array of clone_info elements.

    Args:
        string (str): string to parse into clone_request_list.
        delimiter (str, optional, default = ";"): Delimiter used to split clone_info elements.
        version_action (VersionAction, optional, default=None): Version action use on parsed string.
            Filtering disabled if None.

    Returns:
        clone_request_list (clone_info array) : List of clone_info elements.
    """
    
    get_newest = ( version_action == VersionAction.ALL_NEWEST or
                   version_action == VersionAction.USE_TARGET_IF_ARGUMENT_ELSE_NEWEST )
    
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
    
    clone_info_element = clone_info(url=request.url, branch=request.branch, commit=request.commit,
                                    clone_attempted=False, clone_status=False, clone_path=None)
    return clone_info_element

def execute_clone(clone_info_list, path_source, version_action, force=False, depth=1):
    """
    Clone .

    Args:
        clone_info_list (clone_info array) : List of clone_info elements to clone.
        path_source (str): Path to the clone target.
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
            clone_result = git_clone_url(info.url, path=path_source, force=force, depth=depth, branch=info.branch,
                                         commit=info.commit)
            clone_status = clone_result.status
            clone_path = clone_result.path
            clone_dependencies_path = build_clone_dependencies_path(clone_path)
            info = info._replace(clone_status=clone_status, clone_path=clone_path)
            clone_info_list[i] = info
            if clone_status and os.path.exists(clone_dependencies_path):
                # Load dependencies
                with open(clone_dependencies_path, 'r') as file:
                    dependencies_content = file.read()
                dependency_clone_request_list = string_to_clone_elements(dependencies_content, delimiter="\n",
                                                                         version_action=version_action)
                for request in dependency_clone_request_list:
                    if request.url not in url_array:
                        clone_info_list_addition.append(clone_request_to_info_element(request))
    
    # Add found dependencies to return value
    clone_info_list.extend(clone_info_list_addition)
    
    return clone_info_list
