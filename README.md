# Blinkit Review Analysis Engine

This repository contains an end-to-end AI-powered data pipeline and interactive dashboard for analyzing quick commerce customer reviews (focusing on Blinkit). It automatically scrapes reviews from the App Store, Play Store, Reddit, Quora, and more, cleans the data, clusters it into canonical PM themes using LLMs, and presents it in a beautiful React dashboard.

## Prerequisites
- Node.js v18+
- Python 3.10+
- Groq API Key

## Setup

1. **Clone and Setup Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Setup Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   REDDIT_CLIENT_ID=optional_reddit_client_id
   REDDIT_CLIENT_SECRET=optional_reddit_client_secret
   ```

3. **Install Frontend Dependencies**
   ```bash
   cd dashboard/frontend
   npm install
   ```

## Running the Project

### 1. The Data Pipeline
To execute the entire data pipeline (Scraping -> Cleaning -> Discovery -> Validation):

**On Windows:**
```powershell
.\run_pipeline.ps1
```

**On Mac/Linux:**
```bash
./run_pipeline.sh
```
*Note: This pipeline generates the `reviews_raw.csv`, `themes_raw.json`, and `themes_summary.csv` data artifacts.*

### 2. The Dashboard
To launch the FastAPI backend and Next.js frontend concurrently:

**On Windows:**
```powershell
.\start_dashboard.ps1
```

**On Mac/Linux:**
```bash
./start_dashboard.sh
```

Then visit `http://localhost:3000` in your browser.
