# Imports
import os
import subprocess
import platform

from multiclone.sub.globals import globals_object
from multiclone.sub.path import delete_junction_if_force

########################################################################################################################
# recreate_linked_folder_structure #####################################################################################
########################################################################################################################

def recreate_linked_folder_structure(path_source, path_target, exclusions=None):
    if not os.path.exists(path_source):
        raise ValueError("Source path does not exist.")

    force = globals_object.force

    if exclusions is None:
        exclusions = set()

    for root, dirs, files in os.walk(path_source, topdown=True):
        # Exclude directories from traversal
        dirs[:] = [d for d in dirs if
                   os.path.basename(d) not in exclusions and not os.path.basename(d).startswith(("_", "."))]

        # Create corresponding directories in target path
        for directory in dirs:
            source_dir = os.path.join(root, directory)
            target_dir = os.path.join(path_target, os.path.relpath(source_dir, path_source))
            os.makedirs(target_dir, exist_ok=True)

        # Link files from source to target path
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(path_target, os.path.relpath(source_file, path_source))
            if os.path.basename(target_file) in exclusions or os.path.basename(target_file).startswith(("_", ".")):
                continue
            if force and os.path.exists(target_file):
                os.remove(target_file)
            elif os.path.exists(target_file):
                continue
            os.link(source_file, target_file)

########################################################################################################################
# create_folder_junction ###############################################################################################
########################################################################################################################

# Use "except (subprocess.CalledProcessError, OSError) as e:" to catch errors from this.
def create_folder_junction(target_path, source_path):
    delete_junction_if_force(target_path)  # Remove target if needed and requested

    if os.path.exists(target_path):
        return True

    if platform.system() == 'Windows':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(["cmd.exe", "/c", "mklink", "/j", target_path, source_path], check=True,
                       startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        # Other platforms
        os.symlink(source_path, target_path)
    return True
