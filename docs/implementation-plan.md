# Implementation Plan: AI-Powered Discovery Engine for Quick Commerce

> [!IMPORTANT]
> **Objective:** This document outlines the step-by-step implementation strategy for building the Blinkit Review Analyser. It breaks down the system described in `architecture.md` into actionable development phases, from environment setup to deploying the interactive dashboard.

---

## Phase 1: Project Setup & Environment Initialization
**Goal:** Establish the foundational directory structure, virtual environments, and necessary dependencies.

1. **Initialize Project Repository**
   - Create the root folder `BlinkitReviewAnalyser/`.
   - Initialize Git tracking (`git init`).
   - Set up a Python virtual environment (`python -m venv venv`).
2. **Install Core Dependencies**
   - Data Processing: `pip install pandas numpy beautifulsoup4 praw google-play-scraper`
   - AI/NLP: `pip install transformers sentence-transformers scikit-learn groq`
   - Backend: `pip install fastapi uvicorn pydantic`
   - Frontend: Initialize React/Next.js (`npx create-next-app@latest frontend`)
3. **Establish Directory Structure**
   - Create directories: `src/`, `data/`, `logs/`, `charts/`, `dashboard/`.
4. **Environment Variables Configuration**
   - Create a `.env` file for API keys (e.g., Reddit Client ID, HuggingFace Tokens, etc.).

---

## Phase 2: Data Collection Pipeline (Ingestion)
**Goal:** Build automated scripts to fetch raw user feedback from multiple platforms.

1. **Google Play Store Scraper**
   - Create `src/scrapers/google_play.py`.
   - Use `google-play-scraper` to fetch top 500+ recent Blinkit reviews.
2. **Apple App Store Scraper**
   - Create `src/scrapers/apple_app_store.py`.
   - Parse the iTunes RSS JSON feed for Blinkit reviews.
3. **Reddit API Integration**
   - Create `src/scrapers/reddit_api.py`.
   - Use `praw` to search subreddits (e.g., r/India, r/mumbai, r/gurgaon, r/bangalore) for keywords like "Blinkit", "Zepto", "quick commerce".
4. **Web, Social & Forum Scraping**
   - Create `src/scrapers/forums.py` using BeautifulSoup/Playwright to extract data from:
     - Community forums
     - Social media conversations
     - Product reviews
     - Quick-commerce discussions
5. **Data Unification**
   - Create `src/run_collectors.py` to trigger all scrapers sequentially.
   - Standardize all outputs into the unified `reviews_raw.csv` format (`source`, `date`, `rating`, `text`, `url`).

---

## Phase 3: Data Cleaning & Preprocessing
**Goal:** Maximize the signal-to-noise ratio before NLP processing.

1. **Deduplication Script**
   - Create `src/clean_data.py`.
   - Implement logic to drop exact duplicate texts and cross-posted spam.
2. **Noise Reduction & Filtering**
   - Remove rows where `text` is empty or less than 6 words (e.g., "Good app", "Nice").
   - Strip URLs, promotional codes, and special characters.
3. **Finalize Cleaned Dataset**
   - Overwrite or save the cleaned output back to `data/reviews_raw.csv` ensuring it hits the target of 1,500+ unique discussions.

---

## Phase 4: AI Theme Discovery Engine (NLP)
**Goal:** Extract recurring behavioral themes and cluster them semantically.

1. **Theme Extraction Model**
   - Create `src/extract_themes.py`.
   - Integrate the Groq API for ultra-fast, cloud-based LLM theme extraction and analysis.
2. **Semantic Clustering**
   - Generate embeddings for all reviews in `reviews_raw.csv`.
   - Use K-Means or HDBSCAN to cluster semantically similar reviews into topics (e.g., "Delivery Speed", "Missing Items", "App UI").
3. **Theme Merging & Export**
   - Map clusters to canonical theme names.
   - Export intermediate clustered data to `data/themes_raw.json`.

---

## Phase 5: Theme Validation & Aggregation
**Goal:** Ensure AI insights are grounded in hard evidence and calculate occurrence metrics.

1. **Keyword-Based Validation**
   - Create `src/validate_themes.py`.
   - Extract top keywords from each AI-generated cluster.
   - Scan `reviews_raw.csv` to count the exact percentage of reviews containing these keywords (`validation_pct`).
2. **Aggregation & Ranking**
   - Calculate total frequency and the number of distinct sources for each theme.
   - Rank the top 10 recurring themes.
3. **Generate Final Outputs**
   - Export `data/themes_summary.csv` containing Theme Name, Frequency, Source Count, and Validation Pct.
   - Auto-generate `data/presentation_insights.txt` formatting the insights into human-readable sentences for PMs.

---

## Phase 6: Interactive Dashboard Development
**Goal:** Provide a clean, user-friendly interface and integrate Groq for fast LLM generation.

1. **Backend Development (FastAPI)**
   - Create `dashboard/backend/main.py`.
   - Expose endpoints to serve `themes_summary.csv` and `reviews_raw.csv` as JSON.
   - Integrate Groq API endpoints for on-the-fly, fast LLM generation of dynamic PM insights.
   - Create search/filter endpoints.
2. **Frontend Development (React/Next.js)**
   - Set up the main dashboard page (`dashboard/frontend/src/pages/index.js`).
   - **Metrics Overview:** Implement summary cards (Total Reviews, Top Theme, Sources).
   - **Visualizations:** Use `Chart.js` or `Recharts` for:
     - Theme Frequency Bar Chart
     - Source Distribution Pie/Doughnut Chart
   - **Theme Explorer:** Build a searchable table/list displaying `themes_summary.csv` data alongside example quotes.
   - **Growth Insights Panel:** Implement a text section displaying the contents of `presentation_insights.txt`.

---

## Phase 7: Final Testing & Deployment Prep
**Goal:** Ensure reproducibility and finalize execution scripts.

1. **End-to-End Pipeline Testing**
   - Run the entire ingestion -> cleaning -> discovery -> validation pipeline sequentially to ensure no breakages.
2. **Create Startup Scripts**
   - Write a master `run_pipeline.sh` bash script to execute python scripts automatically.
   - Write a `start_dashboard.sh` bash script to launch both FastAPI and the React server concurrently.
3. **Documentation**
   - Finalize the `README.md` containing instructions on how to install dependencies, run the pipeline, and start the dashboard.

---

## Phase 8: Automated Data Refresh (Scheduler)
**Goal:** Keep the review data fresh by scraping and re-indexing automatically.

1. **GitHub Actions Setup**
   - Create a GitHub Actions workflow (`.github/workflows/scheduler.yml`) to schedule the data ingestion pipeline.
2. **Timezone Configuration**
   - Configure a `cron` trigger in the workflow to execute exactly at **10:00 AM IST** (04:30 UTC) every day.
3. **Pipeline Execution**
   - The workflow will automatically set up Python, execute `fetch.py`, `parse.py`, and `chunk_and_index.py`, and then explicitly commit and push the updated ChromaDB `data/` folder back to the repository to persist the vector changes.
