"""
Link repository to main.

Returns:
"""
# Imports
import os

from globals import globals_object
from sub.path import delete_path_if_force

# Class: Action_LinkToMain
class Action_LinkToMain:
    def action(self):
        # Setup variables
        source_path = globals_object.action_repo_path
        destination_path = os.path.join(globals_object.path_main, globals_object.action_repo_name)
        indentation = "      "  # Default indentation for post clone actions

        deletion_status = delete_path_if_force(destination_path)

        if deletion_status:
            try:
                # Action to take
                os.symlink(source_path, destination_path)  # Replace with
                status = True
                log_string = f"{indentation}Soft link created: {destination_path} -> {source_path}"
            except OSError as e:
                # Exception handling
                log_string = f"{indentation}Error creating soft link: {e}"
                status = False
        else:
            log_string = f"{indentation}Failed to delete for linking: {destination_path}"
            status = False

        # Return results
        globals_object.pca_log_add(log_string)
        return status
