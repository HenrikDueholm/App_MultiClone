# Imports
import os

from globals import globals_object
from sub.path import delete_path_if_force

########################################################################################################################
# Action_CreateFolder ##################################################################################################
########################################################################################################################

"""
Create a folder either relative in Main or absolute anywhere. Supports use of windows environmental variables.

action_data:
    path (str): Absolute path with environmental variable support or path relative to Main.

Returns:
    status (boolean): True if folder created or already found.
"""

class Action_CreateFolder:
    def action(self):
        # Get global data
        path = globals_object.action_data
        main_path = globals_object.path_main

        # Setup variables
        indentation = "      "  # Default indentation for post clone actions

        # Handle environmental variables in path
        try:
            expanded_path = os.path.expandvars(path)
        except TypeError:
            expanded_path = path

        # Sanity check path
        if not expanded_path or not all(char not in '/?%*:|"<>.' for char in expanded_path):
            return False

        # Append to main if relative path
        if not os.path.isabs(expanded_path):
            destination_path = os.path.join(main_path, expanded_path)
        else:
            destination_path = expanded_path

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
