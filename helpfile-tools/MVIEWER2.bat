@echo off
SETLOCAL ENABLEEXTENSIONS

REM Assuming CHM will always be in same folder as MVIEWER2, so:
REM Steal the drive and path from the batch file (parm 0)
REM and name from the 1st or 2nd parameter
REM and attach the CHM extension.

REM MVIEWER2 command line appears to be (SWAGged it!):
REM MVIEWER2 [-i <topic_to_show>] <filename[.mvb]>

if %1==-i (hh.exe "ms-its:%~dp0%~n3.chm::html/%2.htm") else (%~dp0%~n1.chm)
REM if %1==-i (start /B hh.exe "ms-its:%~dp0%~n3.chm::html/%2.htm") else (%~dp0%~n1.chm)

REM Above quotes appear to not be needed even on spaced-out paths...
REM but they feel safer across OSs, so leaving them.
