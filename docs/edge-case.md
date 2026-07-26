# Edge Cases and Corner Scenarios

> [!IMPORTANT]
> **Objective:** This document outlines the potential edge cases, anomalies, and corner scenarios across the entire Blinkit Review Analyser pipeline (as defined in `architecture.md` and `implementation-plan.md`). It also provides mitigation strategies to ensure the system remains resilient and accurate.

---

## 1. Data Collection (Ingestion Pipeline)

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **API Rate Limiting & IP Bans** | Scrapers (Reddit, Google Play) get blocked, resulting in 0 data collected for the day. | Implement exponential backoff, rotating proxies, and strict sleep timers between requests in `run_collectors.py`. |
| **HTML/DOM Structure Changes** | Web scrapers (BeautifulSoup/Playwright) fail because a third-party review site updated its UI. | Use API/RSS feeds wherever possible. Implement try-catch blocks that gracefully skip a failing source rather than crashing the entire pipeline. |
| **Infinite Pagination Loops** | A bug in scraping logic causes the scraper to fetch the same page of reviews infinitely. | Implement a hard limit on the maximum number of pages or reviews to fetch per source (e.g., max 2,000 reviews per run). |
| **Data Volume Surges (Viral Events)** | A viral issue causes a massive influx of 50,000+ reviews in a single day, causing Out-Of-Memory (OOM) errors. | Implement chunked downloading and processing. Stream data directly to disk (`reviews_raw.csv`) instead of holding everything in RAM. |

## 2. Data Cleaning & Preprocessing

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Multilingual & "Hinglish" Reviews** | Reviews in regional languages or mixed Hindi-English bypass NLP theme extraction. | Integrate a lightweight language detection step. Either translate non-English reviews using a free API or explicitly filter for English/Hinglish before LLM processing. |
| **Bot Spam / Near-Duplicates** | Spam bots post identical reviews with one varying character, bypassing exact deduplication. | Use fuzzy string matching (e.g., Levenshtein distance) or cosine similarity on embeddings to drop near-duplicate spam. |
| **Zero Valid Reviews After Filtering** | On a slow day, all fetched reviews might be < 6 words, resulting in an empty dataset. | The pipeline should check for `if df.empty: exit(0)` early and log a warning, rather than crashing downstream scripts. |
| **Malicious Input (XSS)** | A user review contains raw `<script>` tags, potentially compromising the dashboard. | Ensure the FastAPI backend and React frontend strictly sanitize and escape all raw text before rendering. |

## 3. AI Theme Discovery (Groq / NLP Engine)

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Groq API Context Window Exhaustion** | Sending all reviews to the Groq API in one prompt causes a context length error. | Batch reviews into smaller chunks (e.g., 100 reviews per prompt) and perform Map-Reduce: extract themes per batch, then ask Groq to merge the batch themes. |
| **API Outages (503 / 429)** | Groq API goes down or hits rate limits during the scheduled run. | Implement a fallback mechanism to a local, lightweight `sentence-transformers` model if the external Groq API fails after 3 retries. |
| **Clustering Non-Convergence** | The clustering algorithm groups everything into one giant "Miscellaneous" cluster. | Tune HDBSCAN/K-Means hyperparameters. If variance is too low, dynamically adjust the `min_cluster_size`. |
| **Generic Hallucinations** | Groq extracts themes that sound good (e.g., "Customer Satisfaction") but are not actionable. | Enforce strict prompting instructions: "Only extract actionable product or operational issues. Do not generate generic sentiment themes." |

## 4. Theme Validation & Aggregation

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Synonym Mismatches** | The AI generates the theme "Late Delivery", but users wrote "delay" or "not on time", resulting in a 0% validation score. | Instruct Groq to also output an array of 5-10 related keywords/synonyms for each theme, and use all of them in the keyword-matching validation step. |
| **Validation Score is 0%** | The AI hallucinates a theme that simply does not exist in the raw text. | Implement a threshold: any theme in `themes_summary.csv` with a `validation_pct` < 2% is automatically discarded. |

## 5. Dashboard & Presentation

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Stale Data Caching** | The React frontend or FastAPI backend caches old data, not reflecting the latest GitHub Actions run. | Add `Cache-Control: no-cache` headers to API responses and use ETags or timestamp query parameters for the CSV/JSON fetches. |
| **Extremely Long Reviews** | A single review is 2,000 words long, breaking the UI layout of the Theme Explorer. | Implement CSS `text-overflow`, truncation (e.g., "Read more..."), and max-height scrollable containers for raw quotes. |
| **No Data for a Selected Filter** | A PM filters for "Apple App Store" + "Missing Item", yielding 0 results. | Display a user-friendly empty state ("No reviews match these criteria") instead of crashing the visual charts. |

## 6. Automated Data Refresh (GitHub Actions Scheduler)

| Edge Case | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Cron Job Overlap** | Yesterday's data pipeline takes >24 hours, overlapping with today's 10:00 AM IST run, causing data corruption. | Use `concurrency` groups in the `.github/workflows/scheduler.yml` to ensure only one pipeline instance runs at a time. |
| **Git Push Conflicts** | A developer manually modifies the `data/` folder while the GitHub Action is running, causing the automated commit to fail. | Configure the workflow action to do `git pull --rebase` right before committing and pushing, or use a force-push strategy on a dedicated `data-branch`. |
| **Silent API Key Expiry** | The `GROQ_API_KEY` expires, causing silent failures. | Add a notification step (e.g., Slack Webhook or Email) in the GitHub Actions workflow that triggers specifically `if: failure()`. |
