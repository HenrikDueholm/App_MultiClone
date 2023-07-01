import os

# Global object to hold variables
class GlobalVariables:
    def __init__(self):
        # Get the path to the current script (main.py)
        self.path_main_script = os.path.abspath(__file__)

        # Get the directory containing the main.py file
        self.path_main_directory = os.path.dirname(self.path_main_script)

        # Get the directory containing the default post clone plugins
        self.path_default_clone_actions_directory = os.path.join(self.path_main_directory,"clone_actions")

        # Execution variables - Paths
        self.path_main = None
        self.path_source = None

        # Execution variables - Config
        self.force = None

        # Post clone action variables
        self.action_repo_path = None
        self.action_repo_name = None
        self.action_log = []
        self.action_variable_map = {}

    # Post clone action (pca) methods
    def pca_initialize(self, repo_path):
        self.action_repo_path = repo_path
        self.action_repo_name = os.path.basename(repo_path)
        self.action_log = []
        self.action_variable_map = {}

    def pca_variable_add(self, name, value):
        self.action_variable_map[name] = value

    def pca_variable_get(self, name, default=None):
        return self.action_variable_map.get(name, default)

    def pca_log_add(self, log_value):
        self.action_log.append(log_value)

# Create an instance of the GlobalVariables class
globals_object = GlobalVariables()