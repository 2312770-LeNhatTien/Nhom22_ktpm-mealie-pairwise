@echo off
rem Ghi phien ban moi truong vao docs\evidence\H-phien-ban.txt (muc H)
rem Chay sau khi da kich hoat .venv de pip freeze chi co thu vien cua do an
cd /d %~dp0..
set F=docs\evidence\H-phien-ban.txt

echo # Phien ban moi truong chay test>%F%
echo.>>%F%
echo [docker]>>%F%
docker --version>>%F%
echo.>>%F%
echo [image Mealie]>>%F%
docker image inspect ghcr.io/mealie-recipes/mealie:v3.28.0 --format "{{index .RepoDigests 0}}">>%F%
echo.>>%F%
echo [python]>>%F%
python --version>>%F%
echo.>>%F%
echo [pip freeze]>>%F%
pip freeze>>%F%
echo.>>%F%
echo [git commit cua repo nhom]>>%F%
git rev-parse HEAD>>%F%
echo Da ghi %F%
