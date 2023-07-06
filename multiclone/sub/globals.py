import os

# Global object to hold variables
class GlobalVariables:
    def __init__(self):
        # Get the path to the current script (core.py)
        self.path_main_script = os.path.abspath(__file__)

        # Get the directory containing the core.py file
        self.path_main_directory = os.path.dirname(self.path_main_script)

        # Get the directory containing the default post clone plugins
        self.path_default_clone_actions_directory = os.path.join(self.path_main_directory, "../clone_actions")

        # Execution variables - Path and names
        self.path_main = None
        self.path_source = None
        self.path_array = []
        self.repo_name_array = []

        # Execution variables - Config
        self.force = None

        # Post clone action variables
        self.action_repo_path = None
        self.action_repo_name = None
        self.action_data = None
        self.action_log = []
        self.action_variable_map = {}

    # Post clone action (pca) methods
    def pca_initialize(self, repo_path, action_data=None):
        self.action_repo_path = repo_path
        self.action_repo_name = os.path.basename(repo_path)
        self.action_data = action_data
        self.action_log = []
        self.action_variable_map = {}

    def pca_variable_add(self, name, value):
        self.action_variable_map[name] = value

    def pca_variable_get(self, name, default=None):
        return self.action_variable_map.get(name, default)

    def pca_log_add(self, log_value):
        self.action_log.append(log_value)

    def populate_paths(self, paths):
        self.path_array = []
        self.repo_name_array = []
        for path in paths:
            self.path_array.append(path)
            self.repo_name_array.append(os.path.basename(path))


# Create an instance of the GlobalVariables class
globals_object = GlobalVariables()