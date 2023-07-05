# Imports
import os

from multiclone.sub.globals import globals_object
from multiclone.sub.link.link_file_content import recreate_linked_folder_structure

########################################################################################################################
# Action_LinkContentStructureToFolder ##################################################################################
########################################################################################################################

"""
Recreate source folder structure at target using hard links.

action_data:
    path (str): Semicolon separated array of source, target and exclusions.
        target: Uses pre-fix "target=". Point to the folder where the structure should be re-created.
        source (optional): Uses pre-fix "source=". Points to the folder source. Defaults to the repo_name
        exclusions (optional): uses pre-fix "exclusions=". Contains semicolon separated list of file/folder names to exclude.
            Always adds ".git" to exclusions.

Returns:
    status (boolean): True if folder linked.
"""

class Action_LinkContentStructureToFolder:
    def action(self):
        # Get global data
        arguments_string = globals_object.action_data
        main_path = globals_object.path_main
        repo_name = globals_object.action_repo_name

        # Parse argument data from action_data - source
        source_path = globals_object.action_repo_path
        for arg in arguments_string.split(";"):
            if arg.strip().startswith("source="):
                source_path = arg.strip().replace("source=", "")
                break

        # Parse argument data from action_data - target
        target_found = False
        target_path_arg = None
        for arg in arguments_string.split(";"):
            if arg.strip().startswith("target="):
                target_found = True
                target_path_arg = arg.strip().replace("target=", "")
                break
        if not target_found:
            globals_object.pca_log_add(f"{repo_name}: target-argument missing from provided argument string")
            return False
        target_path = os.path.join(main_path, target_path_arg)

        # Parse argument data from action_data - exclusions
        exclusions_split = arguments_string.split("exclusions=")
        if len(exclusions_split) > 1:
            exclusions_arg = exclusions_split[1].split(";")
        else:
            exclusions_arg = []
        exclusions_arg.extend([".git", "README.md"])
        exclusions = exclusions_arg

        # Check if source_path exists
        if not os.path.exists(source_path):
            globals_object.pca_log_add(f"{repo_name}: source path not found")
            return False

        # Re-create structure at target
        recreate_linked_folder_structure(source_path, target_path, exclusions)

        # Return result
        return True
