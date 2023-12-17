rem @echo off
call %~dp0theTop-setenv.bat

if EXIST "%THETOP_HOME%Scripts\activate.bat" goto END_python
:BEGIN_python
    echo ** VirtualEnv: Generate Python Interpreter **
    set TMP_PATH=%PATH%
    set PATH=%THETOP_PREV_PATH%
    virtualenv --no-site-packages %THETOP_HOME%
    echo ** VirtualEnv: Done **
    set PATH=%TMP_PATH%
    set TMP_PATH=
:END_python

REM *** activate the ENV ***
call %THETOP_HOME%Scripts\activate.bat

REM *** install packages ***
pip install zc.buildout

REM *** buildout init ***
if EXIST "%THETOP_HOME%buildout.cfg" goto END_buildout
:BEGIN_buildout
    echo "*** BuildOut: Init ***"
    pushd %THETOP_HOME%
        Scripts\buildout init
		del README.txt
    popd
    echo "*** BuildOut: Done ***"
:END_buildout
