# Imports
import os

from globals import globals_object
from sub.path import sanity_check_path

########################################################################################################################
# Action_CreateFolderInSelf ############################################################################################
########################################################################################################################

"""
Create a folder in own repository. Should be combined with use of .gitignore.

action_data:
    path (str): Relative path to the folder that will be created inside the repository.

Returns:
    status (boolean): True if folder created or already found.
"""

class Action_CreateFolderInSelf:
    def action(self):
        # Get global data
        repo_path = globals_object.action_repo_path
        path = globals_object.action_data

        return create_folder_in_self(repo_path, path)

def create_folder_in_self(repo_path, folder_path):
    # Sanity check path
    if not sanity_check_path(folder_path):
        return False

    # Setup variables
    destination_path = os.path.join(repo_path, folder_path)
    indentation = "      "  # Default indentation for post clone actions

    # Check if folder exists
    if os.path.exists(destination_path):
        log_string = f"{indentation}Folder already found at path: {destination_path}"
        return True

    # Create folder
    try:
        os.makedirs(destination_path)
        status = True
        log_string = f"{indentation}Folder created at path: {destination_path}"
    except OSError as e:
        # Exception handling
        log_string = f"{indentation}Error creating folder: {e}"
        status = False

    # Return results
    globals_object.pca_log_add(log_string)
    return status
