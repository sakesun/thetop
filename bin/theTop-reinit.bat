@echo off
call %~dp0theTop-setenv.bat

rmdir /s/q "%THETOP_HOME%Scripts"
rmdir /s/q "%THETOP_HOME%Lib"
rmdir /s/q "%THETOP_HOME%eggs"
rmdir /s/q "%THETOP_HOME%develop-eggs"
rmdir /s/q "%THETOP_HOME%include"
rmdir /s/q "%THETOP_HOME%parts"

del "%THETOP_HOME%buildout.cfg"

call "%THETOP_BIN%theTop-init.bat"