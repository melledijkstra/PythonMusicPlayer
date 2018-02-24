@echo off

if exist main.spec (
    pyinstaller --onefile main.spec
) else (
    echo main.spec file not found
)
