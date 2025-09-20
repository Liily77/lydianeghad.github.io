@echo off
setlocal
pushd "%~dp0"
chcp 65001 >nul

REM activer l'env
call env-2025\Scripts\activate

REM [NLP + scores]
python scripts\nlp\nlp_step1_sentiment.py || goto :err
python scripts\nlp\nlp_step2_topics_fr.py || goto :err
python scripts\nlp\nlp_step3_influence_fr.py || goto :err
python scripts\nlp\author_centrality.py || goto :err
python scripts\nlp\nlp_step4_absa_light_fr.py || goto :err

REM [freeze -> copier processed -> curated]
if not exist data\curated mkdir data\curated
if not exist data\curated\figures mkdir data\curated\figures

for %%F in (
  avis_with_influence_fr.csv
  centralite_auteur_global.csv
  centralite_auteur_par_hotel.csv
  absa_macro_summary_fr.csv
  absa_macro_by_hotel_counts_fr.csv
  absa_macro_by_hotel_mean_fr.csv
  absa_examples_top_fr.csv
  topics_report_fr.txt
) do (
  if exist data\processed\%%F copy /Y data\processed\%%F data\curated\ >nul
)

if exist data\processed\figures\*.png xcopy /Y /Q data\processed\figures\*.png data\curated\figures\ >nul

REM [QA final]
python scripts\platform\qa_curated.py || goto :err

echo ✔ Recalcul termine (curated a jour)
popd & endlocal & exit /b 0

:err
echo [ERR] Etape echouee (cf. message au-dessus)
popd & endlocal & exit /b 1
