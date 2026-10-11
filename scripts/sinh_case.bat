@echo off
rem Sinh lai cac file test case tu model PICT.
rem Cach dung: mo Command Prompt o thu muc goc cua repo, go: scripts\sinh_case.bat
rem Yeu cau: pict.exe nam trong PATH (tai tu https://github.com/microsoft/pict/releases)

for %%M in (demo household search permissions) do (
    pict models\%%M.txt > cases\%%M.tsv
    echo Da sinh cases\%%M.tsv
)

echo.
echo Thong ke do phu cua tung model:
for %%M in (demo household search permissions) do (
    echo --- %%M
    pict models\%%M.txt /s
)
