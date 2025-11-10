@echo off
REM Usage: scripts\remove_exposed_key.bat "PASTE_EXPOSED_KEY_HERE"

SET EXPOSED_KEY=%1
IF "%EXPOSED_KEY%"=="" (
  ECHO Error: Provide the exposed key as the first argument.
  ECHO Example: scripts\remove_exposed_key.bat AIzaSyXXXX
  EXIT /B 1
)

ECHO Creating temporary replacement file...
SET TMPFILE=%TEMP%\keys_replace.txt
ECHO %EXPOSED_KEY%==^>REMOVED_API_KEY > "%TMPFILE%"

REM Try git-filter-repo first
where git-filter-repo >NUL 2>&1
IF %ERRORLEVEL%==0 (
  ECHO Scrubbing history with git-filter-repo...
  git filter-repo --replace-text "%TMPFILE%"
) ELSE (
  ECHO git-filter-repo not found. Use BFG:
  ECHO  1^) Download BFG: https://rtyley.github.io/bfg-repo-cleaner/
  ECHO  2^) Create a file keys.txt with the exposed key
  ECHO  3^) Run: java -jar bfg.jar --replace-text keys.txt
  ECHO  4^) Then: git reflog expire --expire=now --all
  ECHO             git gc --prune=now --aggressive
)

ECHO Done. If remote exists, force push:
ECHO   git push --force


