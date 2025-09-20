@echo off
setlocal
pushd "%~dp0"
chcp 65001 >nul

REM 1) Activer l'environnement
if exist "env-2025\Scripts\activate" (
  call env-2025\Scripts\activate
) else (
  echo [ERR] env-2025 introuvable.
  exit /b 1
)

REM --- (OPTION) BACKUP avant refresh ---
REM crée un snapshot de data\curated au cas où
for /f %%i in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMdd-HHmmss\")"') do set TS=%%i
if not exist "data\archives" mkdir "data\archives"
xcopy /E /I /Y /Q "data\curated" "data\archives\curated-%TS%" >nul

REM 2) SCRAPING (ajoute les nouveaux avis)
echo [SCRAPE] Hotels...
python scripts\scraping\scrape_google_maps_hotel_1.py || goto :err
python scripts\scraping\scrape_google_maps_hotel_2.py || goto :err
python scripts\scraping\scrape_google_maps_hotel_3.py || goto :err
python scripts\scraping\scrape_google_maps_hotel_4.py || goto :err

REM 3) FUSION + NETTOYAGE
echo [PIPELINE] Fusion + nettoyage...
python scripts\pipeline\concat_avis_google.py || goto :err
python scripts\pipeline\nettoyage.py          || goto :err

REM 4) ANALYSE + CURATED + QA (sans re-scraper)
call run_compute.bat || goto :err

echo.
echo ✔ Rafraichissement complet termine (data\curated mis a jour)
popd & endlocal & exit /b 0

:err
echo.
echo [ERR] Une etape a echoue. Voir le message ci-dessus.
popd & endlocal & exit /b 1
