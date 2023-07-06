@echo off
ECHO Running MultiClone example cloning 2 target repositories with 2 dependent repositories from https://github.com/HenrikDueholm/.
ECHO.
ECHO _______________________________________________________________________
ECHO.
cd..
"MultiClone.exe" https://github.com/HenrikDueholm/LV32.2020..PPL.HDH.Driver.DMM;https://github.com/HenrikDueholm/LV32.2020..PPL.ClassLoader --path "C:\Current projects\Python\Test" --version-action 1 --force --depth 1
pause