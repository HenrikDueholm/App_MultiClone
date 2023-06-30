import importlib
import pkgutil
import inspect
import os

from globals import globals_object

#####################################################################################################
# Core ##############################################################################################
#####################################################################################################

def repository_action(paths, action_source=".postcloneactions", plugin_folders=None):
    """
    Loop over the cloned repositories performing dynamic actions.

    Args:
        paths (str array): Path to the cloned repositories to act on.
        action_source (str, optional, default = ".postcloneactions": The file name to load actions from in the repository root.
        plugin_folders (str, optional, default = None: Path or path array to folders containing plugin actions.

    Returns:
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
                globals_object.pca_initialize(path)  # Reset and initialize global post clone action data
                repo_name = os.path.basename(path)
                print(f"  {repo_name}: {action_source}")

                action_array = action_content.split("\n")
                for action in action_array:
                    try:
                        action_status = run_plugin(plugin_map,action)
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
    return None


#####################################################################################################
# Functions #########################################################################################
#####################################################################################################

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
        files.extend([name for _, name, _ in pkgutil.iter_modules([folder]) if name.endswith('.py')])
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

def run_plugin(plugin_map, plugin_string):
    # ToDo: Add documentation
    plugin_split = plugin_string.split(" ", 1)
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

    # Call reset if it found
    reset_status = True
    if hasattr(plugin_object(), "reset") and callable(getattr(plugin_object(), "reset")):
        try:
            reset_status = plugin_object.reset()
            if not isinstance(reset_status, bool):
                raise TypeError("reset() method must return a boolean value")
        except TypeError:
            reset_status = False

    # Call populate if it found
    populate_status = True
    if hasattr(plugin_object(), "populate") and callable(getattr(plugin_object(), "populate")):
        try:
            populate_status = plugin_object.populate(plugin_data)
            if not isinstance(populate_status, bool):
                raise TypeError("populate() method must return a boolean value")
        except TypeError:
            populate_status = False

    # Call action
    action_status = False
    if reset_status and populate_status:
        try:
            action_status = plugin_object.action()
            if not isinstance(action_status, bool):
                raise TypeError("action() method must return a boolean value")
        except TypeError:
            action_status = False

    return action_status
