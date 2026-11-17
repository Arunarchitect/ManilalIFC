@echo off
setlocal

set SRC=architect
set DST=drafter
set REMOTE=origin

rem project folder: argument 1, else current folder
if not "%~1"=="" (
  pushd "%~dp0%~1" 2>nul
  if errorlevel 1 (
    echo Folder not found: %~dp0%~1
    exit /b 1
  )
) else (
  pushd "%CD%"
)

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo Not a git repo: %CD%
  popd
  exit /b 1
)

echo Repo: %CD%

git reset --hard HEAD
if errorlevel 1 goto fail

git fetch %REMOTE%
if errorlevel 1 goto fail

git checkout %DST%
if errorlevel 1 goto fail

git reset --hard %SRC%
if errorlevel 1 goto fail

git push %REMOTE% %DST% --force-with-lease
if errorlevel 1 goto fail

git checkout %SRC%
if errorlevel 1 goto fail

echo Done: %DST% now matches %SRC%. On branch %SRC%.
popd
exit /b 0

:fail
echo Failed. Check the error above.
popd
exit /b 1