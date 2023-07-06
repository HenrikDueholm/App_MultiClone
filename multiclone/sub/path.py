# Imports
import os
import subprocess

from multiclone.sub.globals import globals_object

def folder_is_junction(path):
    if not os.path.exists(path):
        return False

    try:
        output = subprocess.check_output(['cmd', '/c', 'fsutil', 'reparsepoint', 'query', path], universal_newlines=True)
        is_junction = "Tag value: Mount Point" in output
        return is_junction
    except subprocess.CalledProcessError:
        return False

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

def delete_junction_if_force(path):
    if os.path.exists(path) and globals_object.force and folder_is_junction(path):
        try:
            # Removal using rmdir
            command = ["rmdir", path, "/s", "/q"]
            subprocess.run(command, shell=True)
        except subprocess.CalledProcessError as e:
            return False
    return True

def delete_folder_if_force(path):
    if os.path.exists(path) and globals_object.force:
        try:
            # Removal using rmdir
            command = ["rmdir", path, "/s", "/q"]
            subprocess.run(command, shell=True)
        except subprocess.CalledProcessError as e:
            return False
    return True

def sanity_check_path(path):
    if path is None:
        return False
    for char in path:
        if char in '/?%*|"<>':
            return False
    return True

def build_clone_dependencies_path(repo_path):
    clone_dependencies_path = os.path.join(repo_path, ".dependencies")
    return clone_dependencies_path

########################################################################################################################
# load_dependency_repo_names_from_file #################################################################################
########################################################################################################################

# Imports
from multiclone.sub.clone_url import extract_repo_name

def load_dependency_repo_names_from_file(repo_path):
    dependency_repo_names = []
    clone_dependencies_path = build_clone_dependencies_path(repo_path)

    # Load from file
    if os.path.exists(clone_dependencies_path):
        try:
            with open(clone_dependencies_path, 'r') as file:
                dependencies_content = file.read()
            dependency_string_array = dependencies_content.split("\n")
            for dependency_string in dependency_string_array:
                repo_url = dependency_string.split()[0]
                repo_name = extract_repo_name(repo_url)
                dependency_repo_names.append(repo_name)
        except IOError as e:
            # Print if error. This should never happen, so I will not worry about indentation...
            print(f"Error reading dependency file: {str(e)}")
    return dependency_repo_names
