@echo off
setlocal
rem Sinh lai cac file test case tu 4 model PICT (2-wise va 3-wise, hat giong co dinh /r:22).
rem Cach dung: scripts\sinh_case.bat [all]
rem PICT 3.7.4 is bundled at tools\pict.exe.
rem Add the bundled directory to PATH for this Command Prompt only.
set "PATH=%~dp0..\tools;%PATH%"

if /i "%~1"=="all" goto thu_het

for %%M in (recipe search mealplan shopping) do (
    pict models\%%M.txt /o:2 /r:22 > cases\%%M.o2.tsv
    pict models\%%M.txt /o:3 /r:22 > cases\%%M.o3.tsv
    echo Da sinh cases\%%M.o2.tsv va cases\%%M.o3.tsv
)

echo.
echo Thong ke do phu cua tung model (2-wise):
for %%M in (recipe search mealplan shopping) do (
    echo --- %%M
    pict models\%%M.txt /o:2 /r:22 /s
)

echo.
echo Kiem tra doc lap do phu cap bang script:
python scripts\kiem_tra_cap.py --all
exit /b %errorlevel%

:thu_het
call :sinh_thu_het recipe 8 || exit /b 1
call :sinh_thu_het search 9 || exit /b 1
call :sinh_thu_het mealplan 4 || exit /b 1
call :sinh_thu_het shopping 6 || exit /b 1
exit /b 0

:sinh_thu_het
rem Giu thu tu va ma test cua cac bo case da co.
if exist cases\%1.all.tsv exit /b 0
pict models\%1.txt /o:%2 /r:22 > cases\%1.all.tsv.tmp || exit /b 1
move /y cases\%1.all.tsv.tmp cases\%1.all.tsv >nul
exit /b %errorlevel%
