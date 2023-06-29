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

# Create an instance of the GlobalVariables class
globals_object = GlobalVariables()