"""
Copy this to easily create new clone actions.

Use:
    paths (str array): Path to the cloned repositories to act on.
    action_source (str, optional, default = ".postcloneactions": The file name to load actions from in the repository root.
    plugin_folders (str, optional, default = None: Path or path array to folders containing plugin actions.

Global reads:
    force = globals_object.force  # Get force argument.
    path_main = globals_object.path_main  # Get path to main folder. Where work is meant to be done.
    path_source = globals_object.path_source  # Get path to source folder. Where repositories are cloned to and acted on.

Returns:
"""

from multiclone.sub.globals import globals_object

########################################################################################################################
# Action_LinkToMain ####################################################################################################
########################################################################################################################

"""
Describe what it does.

Returns:
    status (boolean): True if folder linked.
"""

class TemplateAction:
    def action(self):
        # Setup variables
        indentation = "      "  # Default indentation for post clone actions

        try:
            # Action to take

            status = True
            log_string = f"{indentation}Success string"
        except OSError as e:  # Add error cases as needed
            # Exception handling
            log_string = f"{indentation}Error string: {e}"
            status = False
        # Return results
        globals_object.pca_log_add(log_string)
        return status
