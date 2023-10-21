# Imports
import os

# Set directory to root
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get file directory
while current_dir != "/" and not os.path.exists(os.path.join(current_dir, ".git")):  # Detect .git
    current_dir = os.path.dirname(current_dir)

# Check path
if current_dir == "/":
    # .git folder not detected, abort
    print("Unable to find the repository root!")
    exit(1)

# Set directories
os.chdir(current_dir)
path_test = os.path.join(os.path.dirname(current_dir), "Test")

# Imports after directory change
from multiclone.core import main
from multiclone.core import clone_request

# Build clone request
clone_request_list = []
url = 'https://github.com/HenrikDueholm/LV32.2020..PPL.HDH.Driver.DMM'
info = clone_request(url=url, branch=None, commit=None)
clone_request_list.append(info)
url = 'https://github.com/HenrikDueholm/LV32.2020..PPL.ClassLoader'
info = clone_request(url=url, branch=None, commit=None)
clone_request_list.append(info)

# Call MultiClone
main(clone_request_list, path=path_test, force=True, depth=1)
