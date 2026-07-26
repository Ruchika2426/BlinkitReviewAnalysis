import pandas as pd
import re
import os
from datetime import datetime

def clean_text(text):
    if not isinstance(text, str):
        return ""
        
    # 1. Strip URLs (http/https/www)
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # 2. Strip promotional codes (e.g., "Use code BLINKIT50", "referral XYZ123")
    text = re.sub(r'(?i)\b(use code|referral code|coupon code|code)\s+[A-Z0-9]{4,10}\b', '', text)
    
    # 3. Strip special characters (emojis, unicode artifacts) to ensure clean NLP processing
    # We keep standard punctuation required for sentence embeddings (.,!?'")
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Clean up redundant spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def run_cleaning_pipeline():
    """
    Executes Phase 3: Data Cleaning & Preprocessing.
    Filters noise, deduplicates, and standardizes text for the AI engine.
    """
    print(f"[{datetime.now()}] Starting Data Cleaning Pipeline...")
    
    file_path = os.path.join('data', 'reviews_raw.csv')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Run collectors first.")
        return
        
    print(f"Loading raw dataset: {file_path}")
    df = pd.read_csv(file_path)
    initial_count = len(df)
    print(f"Initial record count: {initial_count}")
    
    # 1. Drop rows with completely empty text
    df = df.dropna(subset=['text'])
    
    # 2. Apply Text Cleaning
    print("Applying text cleaning (removing URLs, promo codes, special chars)...")
    df['text'] = df['text'].apply(clean_text)
    
    # Drop rows that became empty after cleaning
    df = df[df['text'].str.strip() != ""]
    
    # 3. Noise Reduction & Filtering (Drop short reviews < 6 words)
    print("Filtering out noisy, short reviews (< 6 words)...")
    df['word_count'] = df['text'].apply(lambda x: len(str(x).split()))
    df = df[df['word_count'] >= 6]
    df = df.drop(columns=['word_count'])
    
    # 3.5 Relevance Filtering (Crucial for Web Search Fallbacks)
    print("Applying strict relevance filter to remove unrelated web results...")
    target_keywords = ['blinkit', 'zepto', 'grofers', 'instamart', 'quick commerce', 'q-commerce', 'swiggy']
    
    def is_relevant(row):
        # App store reviews are inherently relevant to the app
        if row['source'] in ['Apple App Store', 'Google Play Store']:
            return True
        # Web and Social data must explicitly mention a target keyword
        text_lower = str(row['text']).lower()
        return any(keyword in text_lower for keyword in target_keywords)

    df['is_relevant'] = df.apply(is_relevant, axis=1)
    df = df[df['is_relevant'] == True]
    df = df.drop(columns=['is_relevant'])
    
    # 4. Deduplication
    print("Dropping exact duplicate texts (cross-posted spam)...")
    df = df.drop_duplicates(subset=['text'])
    
    final_count = len(df)
    dropped = initial_count - final_count
    
    print(f"\nCleaning complete! Filtered out {dropped} noisy records.")
    print(f"Final high-quality dataset size: {final_count} records.")
    
    # 5. Goal Verification
    if final_count < 1500:
        print(f"\nWARNING: The plan targets 1,500+ unique discussions.")
        print(f"Currently at {final_count}. To reach the goal, please generate Reddit API keys or increase scraper limits!")
        
    # Overwrite the dataset to finalize Phase 3
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"Successfully finalized and overwrote {file_path}")

if __name__ == '__main__':
    run_cleaning_pipeline()
