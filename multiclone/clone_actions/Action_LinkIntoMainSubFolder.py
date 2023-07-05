# Imports
import os

from multiclone.sub.globals import globals_object
from multiclone.sub.path import delete_path_if_force
from multiclone.sub.path import sanity_check_path

########################################################################################################################
# Action_LinkIntoMainSubFolder #########################################################################################
########################################################################################################################

"""
Create a repository link into a main sub-folder.

action_data:
    path (str): Relative path that repository will be linked into as a sub-folder.

Example:
    repo name: Repo1
    destination argument: main\asdf\asd2
    resulting link: main\asdf\asdf2\Repo1

Returns:
    status (boolean): True if folder linked.
"""

class Action_LinkIntoMainSubFolder:
    def action(self):
        # Get global data
        path = globals_object.action_data
        repo_name = globals_object.action_repo_name
        main_path = globals_object.path_main
        source_path = globals_object.action_repo_path

        # Sanity check path
        if not sanity_check_path(path):
            return False

        # Setup variables
        destination_path = os.path.join(os.path.join(main_path, path), repo_name)
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
