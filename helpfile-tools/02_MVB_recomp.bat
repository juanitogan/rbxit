@echo off
SETLOCAL ENABLEEXTENSIONS

set wizdir="HHW wiz"
set moddir="HHW mod"

cd %moddir%\html
wsl ../../../fixhtml.py *.htm
cd ..\..

echo.
echo Now, go back to HHW, close %wizdir%, and open and finish %moddir%.
echo.

pause
