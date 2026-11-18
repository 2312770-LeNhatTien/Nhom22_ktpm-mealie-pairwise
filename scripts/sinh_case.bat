@echo off
rem Sinh lai cac file test case tu 4 model PICT (2-wise va 3-wise, hat giong co dinh /r:22).
rem Cach dung: mo Command Prompt o thu muc goc cua repo, go: scripts\sinh_case.bat
rem Yeu cau: pict.exe nam trong PATH (tai tu https://github.com/microsoft/pict/releases)

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
