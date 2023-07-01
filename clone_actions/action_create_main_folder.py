"""
Create a main folder.

Returns:
    status (boolean): True if folder created or already found.
"""
# Imports
import os

from globals import globals_object
from sub.path import delete_path_if_force

# Class: Action_LinkToMain
class Action_CreateMainFolder:
    def action(self):
        # Get global data
        path = globals_object.action_data
        main_path = globals_object.path_main

        # Sanity check path
        if not path or not all(char not in '/\\?%*:|"<>.' for char in path):
            return False

        # Setup variables
        destination_path = os.path.join(main_path, path)
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
