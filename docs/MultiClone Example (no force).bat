@echo off

setlocal enabledelayedexpansion
set "currentFilePath=%~dp0"
pushd "%currentFilePath%\..\.."
set "rootFolderPath=!CD!"
set "targetPath=!rootFolderPath!\Test"
popd
cd..

ECHO.
ECHO Run MultiClone example:
ECHO - Execute from %CD%
ECHO - Clone 2 target repositories with 2 dependent repositories from https://github.com/HenrikDueholm/
ECHO - Clone to %targetPath%
ECHO - Clone without force option enabled (previously cloned repositories will be skipped)
ECHO.
ECHO _______________________________________________________________________
ECHO.

"MultiClone.exe" https://github.com/HenrikDueholm/LV32.2020..PPL.HDH.Driver.DMM;https://github.com/HenrikDueholm/LV32.2020..PPL.ClassLoader --path "%targetPath%" --version-action 1 --depth 1

ECHO _______________________________________________________________________
ECHO.

endlocal
pause