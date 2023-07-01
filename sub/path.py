import os
import subprocess

from globals import globals_object

def delete_path_if_force(path):
    if os.path.exists(path) and globals_object.force:
        try:
            # Removal using rmdir
            command = ["rmdir", path, "/s", "/q"]
            subprocess.run(command, shell=True)
        except subprocess.CalledProcessError as e:
            return False

    return True
