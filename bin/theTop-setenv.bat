@echo off

REM set common environment variables
set THETOP_BIN=%~dp0
set THETOP_HOME=%THETOP_BIN%..\

REM set PATH
IF "%THETOP_PREV_PATH%" NEQ "" goto END_setpath
:BEGIN_setpath
    set THETOP_PREV_PATH=%PATH%
    set PATH=%THETOP_BIN%;%THETOP_HOME%Scripts\;%SystemRoot%;%SystemRoot%\System32\
:END_setpath

REM set PYTHONPATH
IF "%THETOP_PREV_PYTHONPATH%" NEQ "" goto END_setpythonpath
:BEGIN_setpythonpath
    set THETOP_PREV_PYTHONPATH=%PYTHONPATH%
    set PYTHONPATH=%THETOP_HOME%src\python\
:END_setpythonpath