#!/bin/bash
echo "Starting data pipeline..."
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python src/run_collectors.py
python src/clean_data.py
python src/extract_themes.py
python src/validate_themes.py
echo "Pipeline complete!"
