# Imports
import os

from globals import globals_object
from sub.path import delete_path_if_force

########################################################################################################################
# Action_LinkToMain ####################################################################################################
########################################################################################################################

"""
Link repository to main.

Returns:
    status (boolean): True if folder linked.
"""

class Action_LinkToMain:
    def action(self):
        # Setup variables
        source_path = globals_object.action_repo_path
        destination_path = os.path.join(globals_object.path_main, globals_object.action_repo_name)
        indentation = "      "  # Default indentation for post clone actions

        deletion_status = delete_path_if_force(destination_path)

        if deletion_status and not os.path.exists(destination_path):
            try:
                # Action to take
                os.symlink(source_path, destination_path)  # Replace with
                status = True
                log_string = f"{indentation}Soft link created: {destination_path} -> {source_path}"
            except OSError as e:
                # Exception handling
                log_string = f"{indentation}Error creating soft link: {e}"
                status = False
        elif os.path.exists(destination_path):
            log_string = f"{indentation}Folder found, skip linking to: {destination_path}"
            status = True
        else:
            log_string = f"{indentation}Failed to delete for linking: {destination_path}"
            status = False

        # Return results
        globals_object.pca_log_add(log_string)
        return status
