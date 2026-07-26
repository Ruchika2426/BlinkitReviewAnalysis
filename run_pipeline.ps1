Write-Host "Starting data pipeline..."
.\venv\Scripts\Activate.ps1
python src/run_collectors.py
python src/clean_data.py
python src/extract_themes.py
python src/validate_themes.py
Write-Host "Pipeline complete!"
