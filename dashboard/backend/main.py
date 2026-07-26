import os
import json
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# Load environment variables (API keys)
load_dotenv()

# Initialize FastAPI App
app = FastAPI(title="Blinkit Review Analyser API", version="1.0")

# Configure CORS so the Next.js frontend running on port 3000 can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths safely relative to the project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# Pydantic schema for the Chat endpoint
class GroqQuery(BaseModel):
    prompt: str

class CustomGroqQuery(BaseModel):
    question: str

@app.get("/api/themes")
def get_themes():
    """
    Returns the aggregated theme metrics (Frequency, Source Count, Validation Pct)
    Used to populate the main dashboard charts.
    """
    file_path = os.path.join(DATA_DIR, 'themes_summary.csv')
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Themes summary data not found")
        
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")

@app.get("/api/stats")
def get_stats():
    """
    Returns high-level statistics like total reviews analyzed and number of data sources.
    """
    file_path = os.path.join(DATA_DIR, 'themes_raw.json')
    if not os.path.exists(file_path):
        return {"total_reviews": 0, "sources_count": 0}
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    normalized_sources = set()
    for r in data:
        src = r.get('source')
        if src:
            if 'Reddit' in src:
                normalized_sources.add('Reddit')
            else:
                normalized_sources.add(src)
    
    return {
        "total_reviews": len(data),
        "sources_count": len(normalized_sources),
        "sources_list": sorted(list(normalized_sources))
    }

@app.get("/api/reviews")
def get_reviews(theme: str = Query(None), source: str = Query(None)):
    """
    Returns the raw reviews seamlessly mapped to their AI-generated canonical themes.
    Supports optional query parameters to filter by theme or source platform.
    Used by the 'Theme Explorer' UI.
    """
    file_path = os.path.join(DATA_DIR, 'themes_raw.json')
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Raw themes data not found")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Fix for FastAPI JSON serialization of NaN values
    import math
    def clean_nan(obj):
        if isinstance(obj, float) and math.isnan(obj):
            return None
        elif isinstance(obj, dict):
            return {k: clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nan(i) for i in obj]
        return obj
        
    data = clean_nan(data)
        
    # Apply filters if provided
    if theme:
        data = [r for r in data if r.get('theme') == theme]
    if source:
        data = [r for r in data if r.get('source') == source]
        
    return data

@app.get("/api/insights")
def get_insights():
    """
    Returns the auto-generated PM insights text document.
    """
    file_path = os.path.join(DATA_DIR, 'presentation_insights.txt')
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Insights data not found")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    return {"content": content}

@app.post("/api/ask-groq")
def ask_groq(query: GroqQuery):
    """
    Dynamic PM chat endpoint!
    Provides an on-the-fly connection to the Groq Llama-3.1-8B model.
    Passes context about the top themes so the PM can ask contextual questions.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        keys = ", ".join([k for k in os.environ.keys() if "GROQ" in k or "API" in k])
        raise HTTPException(status_code=500, detail=f"GROQ_API_KEY not configured in .env. Found similar keys: {keys}")
        
    client = Groq(api_key=groq_api_key)
    
    # Load context (the top themes + sample quotes) to ground the LLM
    file_path = os.path.join(DATA_DIR, 'themes_raw.json')
    context = ""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
            
        # Grab up to 3 sample quotes per theme with row numbers
        theme_quotes = {}
        for row_idx, r in enumerate(reviews_data, start=1):
            t = r.get('theme')
            if t:
                if t not in theme_quotes:
                    theme_quotes[t] = []
                if len(theme_quotes[t]) < 2:
                    theme_quotes[t].append((row_idx, r.get('text')))
                
        context = "Here are the top recurring themes identified in our customer reviews dataset, along with real user quotes (and their database Row Numbers) for each:\n"
        for t, quotes in list(theme_quotes.items()): # include all themes to ensure coverage for all 8 questions
            context += f"- Theme: '{t}'.\n"
            for (row_num, text) in quotes:
                clean_q = str(text).replace('\n', ' ').strip()
                context += f"  - Review Row #{row_num}: \"{clean_q}\"\n"
        
    system_prompt = f"""You are an expert Product Manager assistant for a Quick Commerce app (like Blinkit or Zepto).
Context about our specific dataset:
{context}

Answer the PM's question thoughtfully based on this context. Be highly concise, actionable, and focus on growth and UX solutions.
CRITICAL: You MUST answer ALL 8 questions. Do NOT stop early. Your JSON array must contain exactly 8 objects."""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query.prompt}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens=5500,
        )
        return {
            "response": chat_completion.choices[0].message.content,
            "model": "openai/gpt-oss-120b"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask-custom-question")
def ask_custom_question(query: CustomGroqQuery):
    """
    Endpoint for custom AI questions with scope detection and isolated context.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        keys = ", ".join([k for k in os.environ.keys() if "GROQ" in k or "API" in k])
        raise HTTPException(status_code=500, detail=f"GROQ_API_KEY not configured in .env. Found similar keys: {keys}")
    client = Groq(api_key=groq_api_key)

    file_path = os.path.join(DATA_DIR, 'themes_raw.json')
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Review data not found")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)
        
    # Build a representative sample of reviews for context (e.g., up to 40 reviews)
    context_reviews = ""
    for idx, r in enumerate(reviews_data[:40], start=1):
        clean_text = str(r.get('text', '')).replace('\n', ' ').strip()
        channel = str(r.get('source', 'Unknown'))
        context_reviews += f"Review {idx} [{channel}]: \"{clean_text}\"\n"
        
    system_prompt = f"""You are a Product Manager Assistant. You have access to the following review dataset:

{context_reviews}

The user will ask a custom question.

INTELLIGENT SCOPE DETECTION RULES:
1. You must ONLY answer using the provided review dataset. Do NOT hallucinate or use external knowledge.
2. If the question is outside the scope of the available review data (e.g., company financials, politics, unrelated topics, or things not covered by the dataset), you MUST set "outOfScope" to true and provide a polite rejection message.
3. If the question is in scope, you must extract up to 5 findings supported by the reviews.

OUTPUT FORMAT (STRICT JSON ONLY):
If out of scope:
{{
  "outOfScope": true,
  "message": "I couldn't answer that because it is outside the scope of the available review data. This AI can currently answer questions related to: Customer purchase behaviour, Product preferences, Delivery experience, Customer sentiment, etc."
}}

If in scope:
{{
  "outOfScope": false,
  "findings": [
    {{
      "findingNumber": "Finding 1",
      "observation": "[A concise insight answering part of the question.]",
      "evidence": "[Quote or summarize relevant reviews. Mention approximate review counts or patterns.]",
      "impact": "[Explain why this finding is important from a product/business/customer perspective.]"
    }}
  ]
}}

CRITICAL: Output ONLY valid JSON. Escape internal quotes with \\". No markdown wrapping."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query.question}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=4000,
        )
        return {
            "response": chat_completion.choices[0].message.content,
            "model": "openai/gpt-oss-120b"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

