@echo off
rem Chay tren may sach: dung lai Mealie, chay pytest 2 lan, ghi phien ban (muc H).
rem Dung: clone repo moi, mo Command Prompt o thu muc goc roi chay: scripts\may_sach.bat
cd /d %~dp0..

call scripts\dung_lai.bat khong-mo
if errorlevel 1 exit /b 1

python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt

pytest -v --junitxml=docs\evidence\H-may-sach-lan1.xml
pytest -v --junitxml=docs\evidence\H-may-sach-lan2.xml

call scripts\ghi_phien_ban.bat
echo So dat, khong dat, xfail cua hai lan phai giong nhau. Xem hai file docs\evidence\H-may-sach-lan*.xml
