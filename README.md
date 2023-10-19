# MultiClone


MultiClone is a multi-cloning application that allows you to clone multiple repositories and perform post-clone actions in an automated manner.


## Features


- Clone multiple repositories in a combined operation
  - Branch or commit version can be specified for each repository
  - Handle repository versioning with different strategies
  - Clone dependencies recursively using a ".dependencies"-file
- Perform post-clone actions on the cloned repositories
  - Supports side-by-side cloning and linking of dependencies
- Flexible command-line interface for easy usage


## Requirements


- Git must be installed on the system
- Python must be available on the system


## Cloning


To use MultiClone, you need to provide the repository URLs of what to clone (semi-colon separated). You can also specify the versioning strategy, force clone option, and clone depth. Here's an example command:

```cmd:
multiclone "https://github.com/repo1;https://github.com/repo2" --version-action all_newest --force --depth 1 --path "C:\temp\clone"
```


This command will clone the repositories repo1 and repo2 using the "all newest" versioning strategy, force cloning (delete and re-clone), and a depth of 1 commit (note that 1 is default). 

If a ".dependencies"-file is present in the root of a repository the urls from within will be cloned as well. See the "Dependency cloning"-section for more details. 

The repositories will be cloned into "C:\temp\clone\source" from where they will all be linked to "C:\temp\main" unless they contain ".postcloneactions" that specify a different behavior. See the "Post clone actions"-section for more details.

To get more details regarding the arguments and their usage run the application with no arguments.


### Dependency cloning


When a repository has been cloned the ".dependencies"-file is checked for repository dependencies.

A dependency file can consists simply of lines of urls, but it may also be used to specify a specific:

- Branch: Using branch=[branch name]
- Tag: Using branch=tags/[tag string]
- Commit: Using commit=[commit identifier]


These additional dependency details must be in line with the repository they are for. The .split() command is used for separation so whitespace and tabs can be used for separation.

```Example:
https://github.com/repo1 branch=Branch1
https://github.com/repo2	branch=tags/Tag1
https://github.com/repo3 commit=964aea5
```


These additional version details can either be used or ignored depending on the chosen version action. The supported actions are:

- USE_TARGET_IF_ARGUMENT_ELSE_NEWEST: Target details are only used on the repositories specified when calling multiclone. Dependencies will be newest version.
- ALL_NEWEST: All repositories will be cloned to the newest version.
- ALWAYS_USE_TARGET: Target repository will be used for everything.


Note:

- Using the commit argument superseeds the branch argument unless disregarded by the version action setting.
- The branch argument is not influenced by the version action setting, but tags is!
- If the same repository is a dependency to different repositories and they request different versions the resulting version will be the first one cloned. For this the cloning order is important.


### Cloning order


When cloning the following order of cloning is used:

- First all the provided CLI repositories are cloned in order of apperance.
- Then the first CLI repository has all dependencies cloned recursivly followed by the next CLI repository
  - The cloning order of dependencies is from start to end of the ".dependencies"-file


## Post clone actions


When all cloning is complete the repository is scanned for three types of files that are then acted on in order:

- ".postcloneactions_initial"
- ".postcloneactions"
- ".postcloneactions_final"

For most purposes ".postcloneactions" will be sufficient. For custom created ".postcloneactions" the order of the actions might be important. To add custom actions the application must be provided with the "--action-paths"-argument (example: --action-paths "C:\Temp\ActionFolder;MainActions" this will load actions from both the absolute path and from "[main]\MainActions"). For custom plugins to be recognized they must be a class (that is part of a module) and have the method "action" that returns a boolean status.


The default implementation supports the following post clone actions, their needed input arguments and a description are listed below with the following syntax, "[Action name]" "[arguments]" "Example: [argument example]" "Description: [text]":

- "Action_LinkToMain" "" "Example: Action_LinkToMain" "Description: links the folder from source to main. This is the default action if no clone action files are found... so this will never need to be used":
- "Action_CreateMainFolder" "relative path or folder name" "Example: Action_CreateMainFolder TestFolder" "Description: Creates a TestFolder inside of the main folder"
- "Action_LinkToFolder" "target path where folder that repository will be linked into as a sub-folder" "Example1: Action_LinkToFolder C:\temp" "Example2: Action_LinkToFolder TestFolder" "Description: Link the repository as a sub-folder into either an absolute path (example1) or, if relative, into the main folder (Example2)."
- "Action_LinkIntoMainSubFolder" "relative path in main to link into as a sub-folder" "Example: Action_LinkIntoMainSubFolder TestFolder" "Description: Basically the same function as Action_LinkToFolder but now only accepts relative paths that are build on top of main."
- "Action_LinkDependenciesIntoSelf" "target=[repo sub-folder];exclusions=[1];[2]" "Example: Action_LinkDependenciesIntoSelf target=Dependencies;exclusions=Repo1;Repo2" "Description: All dependencies listed in the .dependencies file will be linked into the target sub-folder relative to the repository, except for dependencies that are excluded by name, exclusions are optional."
- "Action_LinkContentStructureToFolder" "source=[sub-folder];target=[relative folder in main];exclusions=[filename1];[filename2]" "Example: Action_LinkContentStructureToFolder target=PPL" "Description: Both source and exclusions are optional. .git and README.md are always added as exclusions. This action will link all the content of the source folder (defaults to the repository root) to the target which should be a sub-folder in the main-folder. Can be extended to support absolute targets if needed..."
- "Action_CreateFolderInSelf" "[relative path in self]" "Example: Action_CreateFolderInSelf TestFolder" "Description: Creates a folder within the repository using the provided relative path."
- "Action_CreateFolder" "[absolute path or path relative to main]" "Example1: Action_CreateFolder C:\Asdf" "Example2: Action_CreateFolder PPL" "Description: Create a folder either in main, if relative, or somewhere else if absolute."


## Source and Build


Source code can be found at [https://github.com/HenrikDueholm/App_MultiClone](https://github.com/HenrikDueholm/App_MultiClone).

Build by running "Build MultiClone Executable". This will build to the "Build_MultiClone"-repository (or folder if not cloned) next to the project folder.

The "Build_MultiClone"-repository can be found at [https://github.com/HenrikDueholm/Build_MultiClone](https://github.com/HenrikDueholm/Build_MultiClone).


## License


MultiClone is licensed under the MIT License. See the LICENSE file for more information.