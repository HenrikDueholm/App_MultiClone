# Imports
import os
import sys

#####################################################################################################
# CLI ###############################################################################################
#####################################################################################################

# Handle CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("")
        print(
            "Usage: python Main.py <url_list> [--path <value>] [--version-action <value>] [--force] [--depth <value>]")
        print(
            "  <url_list>: Semicolon separated list of urls to clone. Specific versions can be acquired by space separated addition of:")
        print("    branch=<branch name>: name of branch to clone")
        print(
            "    commit=<commit>: ID of specific commit to clone (disregards branch if present, however is disregarded itself on use of ALL_NEWEST)")
        print("  --path: Absolute path to roo clone folder (optional, default: os.getcwd())")
        print("  --version-action: Specifies how to handle repository versioning. Accepted values as string or number:")
        print("    1: USE_TARGET_IF_ARGUMENT_ELSE_NEWEST")
        print("    2: ALL_NEWEST")
        print("    3: ALWAYS_USE_TARGET")
        print("  --force: Whether to force clone (optional, default: False)")
        print("  --depth: Clone depth (optional, default: 1)")
        print("")

        sys.exit(1)
    else:
        # Change directory to containing folder.
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Imports after path change
        from multiclone.core import main
        from multiclone.core import string_to_clone_elements
        from multiclone.core import VersionAction


        # Sanity check clone_info - url_list
        url_list = sys.argv[1].split(";")
        if not url_list:
            print("No URLs provided. Exiting...")
            sys.exit(1)

        # Parse url list and build clone_request_list
        clone_request_list = string_to_clone_elements(sys.argv[1], ";")

        # Get path argument
        if "--path" in sys.argv:
            path_index = sys.argv.index("--path")
            if path_index + 1 < len(sys.argv):
                path = sys.argv[path_index + 1]
            else:
                path = None
        else:
            path = None

        # Get version-action argument
        if "--version-action" in sys.argv:
            action_index = sys.argv.index("--version-action")
            if action_index + 1 < len(sys.argv):
                action_value = sys.argv[action_index + 1]
                try:
                    version_action = VersionAction(int(action_value))  # Try parsing as an integer
                except ValueError:
                    version_action = VersionAction[action_value.upper()]  # Treat as a string
            else:
                version_action = VersionAction.USE_TARGET_IF_ARGUMENT_ELSE_NEWEST  # Default value
        else:
            version_action = VersionAction.USE_TARGET_IF_ARGUMENT_ELSE_NEWEST  # Default value

        # Get force argument
        if "--force" in sys.argv:
            force = True
        else:
            force = False

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
        main(clone_request_list, path=path, version_action=version_action, force=force, depth=depth)
