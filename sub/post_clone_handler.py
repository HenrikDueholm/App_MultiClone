import importlib
import inspect
import os
import sys

from globals import globals_object
from clone_actions.Action_LinkToMain import Action_LinkToMain

#####################################################################################################
# Core ##############################################################################################
#####################################################################################################

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

#####################################################################################################
# Functions #########################################################################################
#####################################################################################################

def repository_action(paths, action_source=".postcloneactions", plugin_folders=None):
    """
    Loop over the cloned repositories performing dynamic actions.

    Args:
        paths (str array): Path to the cloned repositories to act on.
        action_source (str, optional, default = ".postcloneactions": The file name to load actions from in the repository root.
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

    # Append default plugins
    plugin_folders.append(globals_object.path_default_clone_actions_directory)

    # Get a list of Python files in the folder
    files = []
    for folder in plugin_folders:
        if os.path.isdir(folder):
            # Add the module directory to the beginning of sys.path
            sys.path.insert(0, str(folder))
            # Get py files in folder
            files.extend([name for name in os.listdir(folder) if name.endswith(".py")])
    files = list(set(files))  # remove duplicate files

    plugin_map = {}
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
