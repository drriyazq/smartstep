@echo off
cmd /k "cd /d C:\Users\drriy\smartstep && echo Fetching... && git fetch origin && git reset --hard origin/main && cd app && flutter pub get && echo. && echo Done! App is up to date."
