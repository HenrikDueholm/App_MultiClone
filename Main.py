import sys
import os

from collections import namedtuple

from App_MultiClone.Clone_URL import git_clone_url
from App_MultiClone.Clone_URL import CloneResult

# Define named tuple type
CloneInfo = namedtuple('CloneInfo', ['url', 'branch', 'commit'])

# Main
def main(clone_info_list, path=None, force=True, depth=1):
    """
    Main function to perform the cloning process.

    Args:
        clone_info_list (list): List of CloneInfo objects.
        path (str, optional, default = os.getcwd()): The absolute clone target path.
        force (bool, optional): Whether to force removal of existing repositories. Default is True.
        depth (int, optional): The depth of the clone (number of commits to include). Default is 1.

    Returns:
        list: List of boolean values indicating the success of each cloning operation.
    """

    # Print config
    print("")
    print("App_MultiClone (version 0.0.1.0)")
    print("")
    print("Config:")
    print(f"  Path: {path}")
    print(f"  Force: {force}")
    print(f"  Depth: {depth}")
    print("")

    # Create folders
    main_path = os.path.join(path, "main")
    if not os.path.exists(main_path):
        os.makedirs(main_path)
    sub_path = os.path.join(path, "sub")
    if not os.path.exists(sub_path):
        os.makedirs(sub_path)
    print("Clone folders:")
    print(f"  Main: {main_path}")
    print(f"  Sub: {sub_path}")
    print("")

    # Clone
    paths = []
    results = []
    for clone_info in clone_info_list:
        clone_result = git_clone_url(clone_info.url, path=main_path, force=force, depth=depth, branch=clone_info.branch, commit=clone_info.commit)
        paths.append(clone_result.path)
        results.append(clone_result.status)

    # Result evaluation
    print("")
    print("Result evaluation:")
    if all(results):
        print("  All clone operations were successful")
    else:
        print("  Some clone operations failed")
    print("")
    return results

#####################################################################################################

# Handle CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("")
        print("Usage: python Main.py <url_list> [--path <value>] [--force <value>] [--depth <value>]")
        print("  --path: Absolute path to roo clone folder (optional, default: os.getcwd())")
        print("  --force: Whether to force clone (optional, default: True)")
        print("  --depth: Clone depth (optional, default: 1)")
        print("")
        sys.exit(1)
    else:
        # Get CloneInfo
        url_list = sys.argv[1].split(';')

        ## Sanity check url_list
        if not url_list:
            print("No URLs provided. Exiting...")
            sys.exit(1)

        ## Parse url list and build CloneInfo_List
        CloneInfo_List = []
        for url in url_list:
            url_parts = url.split()
            url_info = CloneInfo(url=url_parts[0], branch=None, commit=None)
            for part in url_parts[1:]:
                if part.startswith('branch='):
                    url_info = url_info._replace(branch=part[len('branch='):])
                elif part.startswith('commit='):
                    url_info = url_info._replace(commit=part[len('commit='):])
            CloneInfo_List.append(url_info)

        # Get path argument
        if "--path" in sys.argv:
            path_index = sys.argv.index("--path")
            if path_index + 1 < len(sys.argv):
                path = sys.argv[path_index + 1]
            else:
                path = None
        else:
            path = None

        # Get force argument
        if "--force" in sys.argv:
            force_index = sys.argv.index("--force")
            if force_index + 1 < len(sys.argv):
                force = bool(sys.argv[force_index + 1])
            else:
                force = True
        else:
            force = True

        # Get depth argument
        if "--depth" in sys.argv:
            depth_index = sys.argv.index("--depth")
            if depth_index + 1 < len(sys.argv):
                depth = int(sys.argv[depth_index + 1])
            else:
                depth = 1
        else:
            depth = 1

        # Call main
        main(CloneInfo_List, path=path, force=force, depth=depth)
