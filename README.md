# MultiClone

MultiClone is a multi-cloning application that allows you to clone multiple repositories and perform post-clone actions in an automated manner.

## Features

- Clone multiple repositories simultaneously
- Specify branch or commit versions for each repository
- Handle repository versioning with different strategies
- Perform post-clone actions on the cloned repositories
- Supports side-by-side cloning and linking of dependencies
- Flexible command-line interface for easy usage

## Requirements

- Python and Git must be installed on the system. 
- Clone actions using soft links will require elevation!

## Usage

To use MultiClone, you need to provide a list of repository URLs to clone. You can also specify the versioning strategy, force clone option, and clone depth. Here's an example command:

```cmd
multiclone "https://github.com/repo1;https://github.com/repo2" --version-action all_newest --force --depth 1
```

This command will clone the repositories repo1 and repo2 using the "all newest" versioning strategy, force cloning, and a depth of 1 commit.

To get more details regarding the arguments and their usage run the application with no arguments.

## Source and Build

Source code can be found at [https://github.com/HenrikDueholm/App_MultiClone](https://github.com/HenrikDueholm/App_MultiClone).
Build by running "Build MultiClone Executable". This will build to the "Build_MultiClone"-repository (or folder if not cloned) next to the project folder.
The "Build_MultiClone"-repository can be found at [https://github.com/HenrikDueholm/Build_MultiClone](https://github.com/HenrikDueholm/Build_MultiClone).

## License

MultiClone is licensed under the MIT License. See the LICENSE file for more information.