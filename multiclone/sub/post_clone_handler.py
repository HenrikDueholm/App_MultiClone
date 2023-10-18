# System imports
import importlib
import inspect
import os
import sys
import subprocess

# Core imports
from multiclone.sub.globals import globals_object

# Plugin imports
from multiclone.sub.path import sanity_check_path
from multiclone.sub.path import create_folder
from multiclone.sub.link import recreate_linked_folder_structure
from multiclone.sub.path import load_dependency_repo_names_from_file
from multiclone.sub.link import create_folder_junction
from multiclone.sub.path import delete_junction_if_force

########################################################################################################################
# Core #################################################################################################################
########################################################################################################################


def post_clone_action_handler(paths, plugin_folders=None):

    # Check for any clone actions, link to main if none are found
    paths_with_action_initial = []
    paths_with_action = []
    paths_with_action_final = []
    paths_with_action_any = []
    paths_with_no_action = []
    link_status_array = []

    # Populate global with source paths
    globals_object.populate_paths(paths)

    # Look for post clone action types in paths
    for path in paths:
        path_action_initial = os.path.join(path, ".postcloneactions_initial")
        path_action = os.path.join(path, ".postcloneactions")
        path_action_final = os.path.join(path, ".postcloneactions_final")

        action_found = False

        if os.path.exists(path_action_initial):
            paths_with_action_initial.append(path)
            action_found = True

        if os.path.exists(path_action):
            paths_with_action.append(path)
            action_found = True

        if os.path.exists(path_action_final):
            paths_with_action_final.append(path)
            action_found = True

        if not action_found:
            paths_with_no_action.append(path)
        else:
            paths_with_action_any.append(path)

    if paths_with_no_action:
        print("Link non-action repositories to main")
        for path in paths_with_no_action:
            # Link repository to main
            globals_object.pca_initialize(path)  # Populate global with current path
            link_object = Action_LinkToMain()
            link_status = link_object.action()
            link_status_array.append(link_status)
            if not link_status and globals_object.action_log:
                print("  Linking failure encountered - Log:")
                for log_element in globals_object.action_log:
                    print(f"    {log_element}")
            elif not link_status:
                print("  Linking failure encountered")

    if paths_with_action_any:
        any_actions_found = True
        # At least one path contains actions, handled in individual cases
    elif not paths_with_action_any and all(link_status_array):
        print("No failures during link actions")
        print("")
        return True
    elif not paths_with_action_any and not all(link_status_array):
        print("No clone actions detected - Not all repositories successfully linked to main!")
        print("")
        return False

    # Initial action
    action_initial_status = True
    if paths_with_action_initial:
        print("Run initial repository post clone actions:")
        # ToDo: Add plugin_folders config (external config?)
        action_initial_status = repository_action(
            paths=paths_with_action_initial,
            action_source=".postcloneactions_initial",
            plugin_folders=plugin_folders
        )
        if action_initial_status:
            print("Initial post clone actions run successfully")
        else:
            print("Initial post clone actions did not all run successfully")
        print("")

    # Action
    action_status = True
    if paths_with_action:
        print("Run repository post clone actions:")
        # ToDo: Add plugin_folders config (external config?)
        action_status = repository_action(
            paths=paths_with_action,
            action_source=".postcloneactions",
            plugin_folders=plugin_folders
        )
        if action_status:
            print("Post clone actions run successfully")
        else:
            print("Post clone actions did not all run successfully")
        print("")

    # Final action
    action_final_status = True
    if paths_with_action_final:
        print("Run final repository post clone actions:")
        # ToDo: Add plugin_folders config (external config?)
        action_final_status = repository_action(
            paths=paths_with_action_final,
            action_source=".postcloneactions_final",
            plugin_folders=plugin_folders
        )
        if action_final_status:
            print("Final post clone actions run successfully")
        else:
            print("Final post clone actions did not all run successfully")
        print("")

    return action_initial_status and action_status and action_final_status

########################################################################################################################
# Functions ############################################################################################################
########################################################################################################################


def repository_action(paths, action_source=".postcloneactions", plugin_folders=None):
    """
    Loop over the cloned repositories performing dynamic actions.

    Args:
        paths (str array): Path to the cloned repositories to act on.
        action_source (str, optional, default = ".postcloneactions":
                                                The file name to load actions from in the repository root.
        plugin_folders (str, optional, default = None: Path or path array to folders containing plugin actions.

    """
    # ToDo: Add print
    plugin_map = load_plugins(plugin_folders=plugin_folders)

    # For every repository
    summary_array = []
    for path in paths:
        path_clone_actions = os.path.join(path, action_source)

        # Action_source found?
        if os.path.exists(path_clone_actions):
            action_array = []
            status_array = []

            # Load post clone actions
            with open(path_clone_actions, 'r') as file:
                action_content = file.read()
            if action_content:
                repo_name = os.path.basename(path)
                print(f"  {repo_name}: {action_source}")

                action_array = action_content.split("\n",)
                for action in action_array:
                    try:
                        action_status = run_plugin(plugin_map, action, path)
                    except TypeError:
                        action_status = False

                    status_array.append(action_status)
                    if not action_status and globals_object.action_log:
                        print("    Action failure encountered - dump log:")
                        for log_element in globals_object.action_log:
                            print(f"      {log_element}")
                    elif not action_status:
                        print("    Action failure encountered")

            summary_array.append(all(status_array))
        else:
            summary_array.append(True)

    return all(summary_array)


def load_plugins(plugin_folders=None):
    # ToDo: Add documentation
    # Parse plugin_folders
    if plugin_folders is None:
        plugin_folders = []
    elif isinstance(plugin_folders, str):
        plugin_folders = [plugin_folders]
    elif isinstance(plugin_folders, list):
        pass  # plugin_folders is already a list
    else:
        # Handle the case when plugin_folders is neither a string nor a list
        raise ValueError("plugin_folders should be a string or a list of strings")

    # Get a list of Python files in the folder
    files = []
    for folder in plugin_folders:
        if os.path.isdir(folder):
            # Add the module directory to the beginning of sys.path
            sys.path.insert(0, str(folder))
            # Get py files in folder
            files.append([name for name in os.listdir(folder) if name.endswith(".py")])

    files = list(set(files))  # remove duplicate files

    plugin_map = {}

    # Load default plugins
    module_name = __name__
    module = importlib.import_module(module_name)

    # Search for the class in the module
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and hasattr(obj(), "action") and callable(getattr(obj(), "action")):
            plugin_map[name] = obj()

    # Load dynamic plugins
    for file in files:
        module_name = os.path.splitext(file)[0]

        # Import the module
        module = importlib.import_module(module_name)

        # Search for the class in the module
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj(), "action") and callable(getattr(obj(), "action")):
                plugin_map[name] = obj()

    return plugin_map


def run_plugin(plugin_map, plugin_string, repo_path):
    # ToDo: Add documentation
    plugin_split = plugin_string.split(" ", 1)  # Get name by splitting ón first space.
    plugin_name = plugin_split[0]
    if len(plugin_split) > 1:
        plugin_data = plugin_split[1]
    else:
        plugin_data = ""

    # get plugin object
    if plugin_name in plugin_map:
        plugin_object = plugin_map[plugin_name]
    else:
        # ToDo: Add print
        return False

    # Call action
    action_status = False
    try:
        globals_object.pca_initialize(repo_path, plugin_data)  # Reset and initialize global post clone action data
        action_status = plugin_object.action()
        if not isinstance(action_status, bool):
            raise TypeError("action() method must return a boolean value")
    except TypeError:
        action_status = False

    return action_status

########################################################################################################################
# Plugins ##############################################################################################################
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
        if not sanity_check_path(expanded_path):
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
            status = create_folder(destination_path)
            log_string = f"{indentation}Folder created at path: {destination_path}"
        except OSError as e:
            # Exception handling
            log_string = f"{indentation}Error creating folder: {e}"
            status = False

        # Return results
        globals_object.pca_log_add(log_string)
        return status

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
        status = create_folder(destination_path)
        log_string = f"{indentation}Folder created at path: {destination_path}"
    except OSError as e:
        # Exception handling
        log_string = f"{indentation}Error creating folder: {e}"
        status = False

    # Return results
    globals_object.pca_log_add(log_string)
    return status

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
        valid_target = create_folder(target_path)
        if not valid_target:
            globals_object.pca_log_add(f"{repo_name}: Failed to find or create target folder")
            return False

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

        deletion_status = delete_junction_if_force(destination_path)

        if deletion_status and not os.path.exists(destination_path):
            try:
                # Action to take
                status = create_folder_junction(destination_path, source_path)
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

# Action_LinkToFolder ##################################################################################################
########################################################################################################################


"""
Link repository into target folder. If target is not provided it defaults to the main folder.

action_data:
    path (str): Target path that repository will be linked into as a sub-folder.

Returns:
    status (boolean): True if folder linked or already exists.
"""


class Action_LinkToFolder:
    def action(self):
        # Setup variables
        target_path = globals_object.action_data
        source_path = globals_object.action_repo_path
        fallback_path = globals_object.path_main

        return create_soft_link(target_path, source_path, fallback_path)


def create_soft_link(target_path, source_path, fallback_path=None):

    """
    Link source path to target_path\repo_name. If target is not provided it defaults to the main folder.

    action_data:
        path (str): Target path that repository will be linked into as a sub-folder.

    Returns:
        status (boolean): True if folder linked or already exists.
    """

    # Set default value for fallback_path
    if fallback_path is None:
        fallback_path = globals_object.path_main

    # Setup variables
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
    source_repo_name = os.path.basename(source_path)
    expanded_repo_path = os.path.join(expanded_path, source_repo_name)

    # Append to main if relative path
    if not os.path.isabs(expanded_repo_path):
        destination_path = os.path.join(fallback_path, expanded_repo_path)
    else:
        destination_path = expanded_repo_path

    deletion_status = delete_junction_if_force(destination_path)

    if deletion_status and not os.path.exists(destination_path):
        try:
            status = create_folder_junction(destination_path, source_path)
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

        deletion_status = delete_junction_if_force(destination_path)

        if deletion_status and not os.path.exists(destination_path):
            try:
                status = create_folder_junction(destination_path, source_path)
                log_string = f"{indentation}Soft link created: {destination_path} -> {source_path}"
            except (subprocess.CalledProcessError, OSError) as e:
                # Exception handling
                log_string = f"{indentation}Error creating link: {e}"
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

# Action_CreateMainFolder ##############################################################################################
########################################################################################################################

"""
Create a folder in main.

action_data:
    path (str): Relative path that will be joined with main.

Returns:
    status (boolean): True if folder created or already found.
"""

class Action_CreateMainFolder:
    def action(self):
        # Get global data
        path = globals_object.action_data
        main_path = globals_object.path_main

        # Sanity check path
        if not sanity_check_path(path):
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
            status = create_folder(destination_path)
            log_string = f"{indentation}Folder created at path: {destination_path}"
        except OSError as e:
            # Exception handling
            log_string = f"{indentation}Error creating folder: {e}"
            status = False

        # Return results
        globals_object.pca_log_add(log_string)
        return status