@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "DRY_RUN=0"
if /I "%~1"=="--dry-run" set "DRY_RUN=1"

echo [1/5] Checking git availability...
where git >nul 2>nul
if errorlevel 1 (
    echo Git is not installed or not in PATH.
    goto :fail
)

echo [2/5] Detecting current branch...
for /f "usebackq delims=" %%i in (`git branch --show-current`) do set "CURRENT_BRANCH=%%i"
if not defined CURRENT_BRANCH (
    echo Failed to detect the current branch.
    goto :fail
)

if /I not "!CURRENT_BRANCH!"=="main" if /I not "!CURRENT_BRANCH!"=="master" (
    echo Current branch is "!CURRENT_BRANCH!".
    echo This deploy script only pushes from main or master.
    goto :fail
)

echo [3/5] Staging changes...
if "%DRY_RUN%"=="1" (
    echo DRY RUN: git add -A
) else (
    git add -A
    if errorlevel 1 goto :fail
)

echo [4/5] Creating commit when needed...
set "COMMIT_MSG=Update blog on %date% %time%"
if "%DRY_RUN%"=="1" (
    echo DRY RUN: git commit -m "!COMMIT_MSG!"
    echo DRY RUN: git push -u origin !CURRENT_BRANCH!
    goto :success
)

git diff --cached --quiet --exit-code
if errorlevel 1 (
    git commit -m "!COMMIT_MSG!"
    if errorlevel 1 goto :fail
) else (
    echo No file changes detected. Will only push existing local commits if any.
)

echo [5/5] Pushing to GitHub...
git push -u origin !CURRENT_BRANCH!
if errorlevel 1 goto :fail

:success
echo Done.
pause
exit /b 0

:fail
echo Deployment script failed.
pause
exit /b 1
