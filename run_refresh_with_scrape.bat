@echo off
setlocal
pushd "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

REM --- Rendre la racine visible pour les imports "scripts.*"
set PYTHONPATH=%CD%

REM --- 1) Activer l'environnement (CMD)
if exist "env-2025\Scripts\activate.bat" (
  call "env-2025\Scripts\activate.bat"
) else (
  echo [ERR] env-2025 introuvable.
  popd & endlocal & exit /b 1
)

REM --- (OPTION) BACKUP avant refresh : snapshot de data\curated
for /f %%i in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMdd-HHmmss\")"') do set "TS=%%i"
if not exist "data\archives" mkdir "data\archives"
if exist "data\curated" xcopy /E /I /Y /Q "data\curated" "data\archives\curated-%TS%\" >nul

REM --- 2) SCRAPING (delta + top-up récent)
echo [SCRAPE] Hotels...
python -m scripts.scraping.scrape_google_maps_hotel_1 || goto :err
python -m scripts.scraping.scrape_google_maps_hotel_2 || goto :err
python -m scripts.scraping.scrape_google_maps_hotel_3 || goto :err
python -m scripts.scraping.scrape_google_maps_hotel_4 || goto :err

REM --- 3) FUSION + NETTOYAGE
echo [PIPELINE] Fusion + nettoyage...
python -m scripts.pipeline.concat_avis_google || goto :err
python -m scripts.pipeline.nettoyage          || goto :err

REM --- 4) ANALYSE + CURATED + QA (sans re-scraper)
call run_compute.bat || goto :err

echo.
echo ✔ Rafraîchissement complet terminé (data\curated mis à jour)
popd & endlocal & exit /b 0

:err
echo.
echo [ERR] Une étape a échoué. Voir le message ci-dessus.
popd & endlocal & exit /b 1
