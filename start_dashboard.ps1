Write-Host "Starting FastAPI Backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\Activate.ps1; uvicorn dashboard.backend.main:app --host 0.0.0.0 --port 8000"

Write-Host "Starting Next.js Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd dashboard\frontend; npm run dev"
