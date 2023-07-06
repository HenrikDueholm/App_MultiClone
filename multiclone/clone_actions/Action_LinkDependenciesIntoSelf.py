# Imports
import os

from multiclone.sub.globals import globals_object
from multiclone.sub.path import load_dependency_repo_names_from_file
from multiclone.clone_actions.Action_CreateFolderInSelf import create_folder_in_self
from multiclone.clone_actions.Action_LinkToFolder import create_soft_link
from multiclone.sub.link import create_folder_junction

########################################################################################################################
# Action_LinkDependenciesIntoSelf ######################################################################################
########################################################################################################################

"""
Link all non excluded dependencies into the active repository target folder.

action_data:
    path (str): Semicolon separated array of target and exclusions.
        target: Uses pre-fix "target=". Relative path to the folder that will be linked to inside the repository.
            Target is created if it is not found.
        exclusions (optional): Uses pre-fix "exclusions=". Contains semicolon separated list repo-names to exclude.

Returns:
    status (boolean): True if all dependencies linked.
"""

class Action_LinkDependenciesIntoSelf:
    def action(self):
        # Get global data
        arguments_string = globals_object.action_data
        repo_path = globals_object.action_repo_path
        repo_name = globals_object.action_repo_name
        source_path = globals_object.path_source

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

        # Parse argument data from action_data - exclusions
        exclusions_split = arguments_string.split("exclusions=")
        if len(exclusions_split) > 1:
            exclusions_arg = exclusions_split[1].split(";")
        else:
            exclusions_arg = []
        exclusions = list(exclusions_arg)

        # Create target if needed
        if not create_folder_in_self(repo_path, target_path_arg):
            return False
        target_path = os.path.join(repo_path, target_path_arg)

        # Get dependencies
        dependencies = load_dependency_repo_names_from_file(repo_path)

        # Link dependencies to target if not in exclusions
        status_array = []
        for dependency in dependencies:
            repo_source = os.path.join(source_path, dependency)
            if dependency not in exclusions and os.path.exists(repo_source):
                status = create_soft_link(target_path, repo_source)
                status_array.append(status)
            elif not os.path.exists(repo_source):
                status_array.append(False)
                globals_object.pca_log_add(f"{repo_name}: source path ({dependency}) not found")

        # Return result
        return all(status_array)
