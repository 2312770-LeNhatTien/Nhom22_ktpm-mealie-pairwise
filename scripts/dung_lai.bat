@echo off
rem Dung lai Mealie sach bang mot lenh: python/docker phai co san.
rem CANH BAO: docker compose down -v xoa het du lieu Mealie tren may (ke ca tai khoan nhom22).
rem Dung: scripts\dung_lai.bat          (xong thi mo cua so de chay pytest)
rem       scripts\dung_lai.bat khong-mo (xong thi thoat, dung khi chay thu)
cd /d %~dp0..
echo Bat dau: %time%

docker compose down -v
docker compose up -d --wait
if errorlevel 1 (
  echo Mealie chua len. Da bat Docker Desktop chua? Xem log: docker compose logs mealie
  exit /b 1
)

rem Sau khi xoa du lieu, Mealie chi con tai khoan mac dinh nen dung tai khoan nay
set MEALIE_URL=http://localhost:9925
set MEALIE_USER=changeme@example.com
set MEALIE_PASS=MyPassword
set MEALIE_EMAIL=changeme@example.com
set MEALIE_PASSWORD=MyPassword

python scripts\chuan_bi_muc_c.py seed
if errorlevel 1 (
  echo Nap du lieu mau bi loi
  exit /b 1
)
echo Xong: %time%

if "%1"=="khong-mo" exit /b 0
cmd /k echo Mealie san sang. Chay: pytest
