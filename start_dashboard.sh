#!/bin/bash
echo "Starting FastAPI Backend..."
source venv/bin/activate
uvicorn dashboard.backend.main:app --host 0.0.0.0 --port 8000 &

echo "Starting Next.js Frontend..."
cd dashboard/frontend
npm run dev
