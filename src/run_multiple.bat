@REM @echo off
@REM set /a i=0
@REM :loop
@REM if %i%==100 goto end
@REM python .\src\run.py -i %i%
@REM set /a i+=1
@REM goto loop
@REM :end

@echo off
setlocal EnableDelayedExpansion
set "array=4 27 39 41 53 64 70 77 90"
for %%i in (%array%) do (
    set /a "j=%%i-1"
    python .\src\run.py -i %%i
    @REM python .\src\run.py -i !j!
)