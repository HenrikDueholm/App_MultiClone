# Imports
import os

from globals import globals_object
from sub.path import delete_path_if_force
from sub.path import sanity_check_path

########################################################################################################################
# Action_LinkToFolder ##################################################################################################
########################################################################################################################

"""
Link repository into target folder. If target is not provided it defaults to the main folder.

Returns:
    status (boolean): True if folder linked or already exists.
"""

class Action_LinkToFolder:
    def action(self):
        # Setup variables
        source_path = globals_object.action_repo_path
        target_path = globals_object.action_data
        main_path = globals_object.path_main
        indentation = "      "  # Default indentation for post clone actions

        # Handle environmental variables in path
        try:
            expanded_path = os.path.expandvars(target_path)
        except TypeError:
            expanded_path = target_path

        # Sanity check path
        if not sanity_check_path(expanded_path):
            return False

        # Add source to repository
        expanded_repo_path = os.path.join(expanded_path, globals_object.action_repo_name)

        # Append to main if relative path
        if not os.path.isabs(expanded_repo_path):
            destination_path = os.path.join(main_path, expanded_repo_path)
        else:
            destination_path = expanded_repo_path

        deletion_status = delete_path_if_force(destination_path)

        if deletion_status and not os.path.exists(destination_path):
            try:
                os.symlink(source_path, destination_path)
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
