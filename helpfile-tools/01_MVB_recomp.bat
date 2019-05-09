@echo off
SETLOCAL ENABLEEXTENSIONS

REM ======================================================================
REM CHANGE ME:
REM ----------------------------------------------------------------------
set helpdecoexe="D:\GamesTest\WinHelp Tools\HELPDECO\HELPDECO.EXE"
REM ======================================================================

echo ======================================================================
echo This batch assumes a parent/child folder structure like this:
echo     Parent:
echo         fixtrf.py
echo         fixhtml.py
echo         HHStyles.css
echo         SOMEFILE:
echo             SOMEFILE.MVB        (only one help file per folder)
echo             01_MVB_recomp.bat
echo             02_MVB_recomp.bat
echo ======================================================================

REM Process only the last help file found in the folder (should be only one).
REM TODO: FOR %%f IN (*.MVB *.HLP) DO set helpfile=%%f
for %%f in (*.MVB) do set helpfile=%%f
if "%helpfile%"=="" (
	echo *** No help file found: *.MVB ***
	echo Aborting...
	goto end
)

REM Assumes always a 3-letter suffix on helpfile:

set helpfileprefix=%helpfile:~0,-4%

REM set outdir="%helpfile:~0,-4% %helpfile:~-3,3% decompile"
set outdir="MVB decompile"
set wizdir="HHW wiz"
set moddir="HHW mod"
set bakdir="HHW _bak_"

%helpdecoexe% %helpfile%
REM Don't recall at the moment if *.CNT file actually needed:
%helpdecoexe% %helpfile% /c
REM The CNT file is not needed but it can help with decoding randomized topic names.

copy *.MVP *.HPJ
copy *.RTF *.org.RTF

mkdir %outdir%
move /Y *.MVP %outdir%
move /Y *.HPJ %outdir%
move /Y *.RTF %outdir%
move /Y *.CNT %outdir%
move /Y *.bmp %outdir%
move /Y *.shg %outdir%

echo.

wsl ../fixrtf.py %outdir%/%helpfileprefix%.org.RTF %outdir%/%helpfileprefix%.RTF

mkdir %wizdir%
mkdir %moddir%
mkdir %bakdir%
echo dummy file > %wizdir%\%helpfileprefix%.hhp
echo dummy file > %moddir%\%helpfileprefix%.hhp

copy ..\HHStyles.css %moddir%

echo.
echo Now, move on to the HHW and HHPMod steps before returning to 02_MVB_recomp.bat.
echo.

:end
pause
