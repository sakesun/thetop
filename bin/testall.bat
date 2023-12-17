@echo off

call %~dp0theTop-setenv.bat

python -m unittest discover -v -s %THETOP_HOME%src\python
