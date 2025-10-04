@echo off
setlocal
pushd "%~dp0"
chcp 65001 >nul

REM --- Rendre la racine visible pour les imports "scripts.*"
set PYTHONPATH=%CD%

REM --- 0) Activer l'environnement (CMD). OK si déjà actif.
if exist "env-2025\Scripts\activate.bat" (
  call "env-2025\Scripts\activate.bat"
) else (
  echo [WARN] activate.bat introuvable. On continue si le venv est deja actif.
)

REM --- 1) NLP + scores (on se place dans scripts\nlp pour respecter ../../data/...)
pushd "scripts\nlp"
python nlp_step1_sentiment.py        || goto :err_out_nlp
python nlp_step2_topics_fr.py        || goto :err_out_nlp
python nlp_step3_influence_fr.py     || goto :err_out_nlp
REM python author_centrality.py      || goto :err_out_nlp   (désactivé si non utilisé)
popd

REM --- 1bis) ABSA (toujours depuis la racine)
python -m scripts.nlp.nlp_step4_absa_light_fr    || goto :err

REM --- 2) Freeze curated (copie processed -> curated)
if not exist "data\curated" mkdir "data\curated"
if not exist "data\curated\figures" mkdir "data\curated\figures"

for %%F in (
  avis_with_influence_fr.csv
  absa_macro_summary_fr.csv
  absa_macro_by_hotel_counts_fr.csv
  absa_macro_by_hotel_mean_fr.csv
  absa_examples_top_fr.csv
  topics_report_fr.txt
) do (
  if exist "data\processed\%%F" copy /Y "data\processed\%%F" "data\curated\" >nul
)

if exist "data\processed\figures\*.png" xcopy /Y /Q "data\processed\figures\*.png" "data\curated\figures\" >nul

REM --- 3) QA final
python -m scripts.platform.qa_curated            || goto :err

echo.
echo ✔ Recalcul termine (curated a jour)
popd & endlocal & exit /b 0

:err_out_nlp
popd
:err
echo.
echo [ERR] Etape echouee (cf. message au-dessus)
popd & endlocal & exit /b 1
