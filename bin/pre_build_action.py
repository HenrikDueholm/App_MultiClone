import shutil
import os

files_to_copy = ['README.md', 'CHANGES.txt', 'LICENSE']
folders_to_copy = ['docs']

build_dir = '../Build_MultiClone'

for file in files_to_copy:
    source_file = file
    target_file = os.path.join(build_dir, file)

    if os.path.exists(target_file):
        os.remove(target_file)

    shutil.copy(source_file, target_file)

for folder in folders_to_copy:
    source_folder = folder
    target_folder = os.path.join(build_dir, folder)

    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)

    shutil.copytree(source_folder, target_folder)
