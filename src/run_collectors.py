import os
import pandas as pd
from datetime import datetime

# Import individual scrapers
from scrapers.google_play import scrape_google_play_reviews
from scrapers.apple_app_store import scrape_apple_app_store_reviews
from scrapers.reddit_api import scrape_reddit_discussions
from scrapers.forums import scrape_web_and_social

def run_all_collectors():
    """
    Triggers all scrapers sequentially and unifies their data into a single master dataset.
    """
    print(f"[{datetime.now()}] 🚀 Starting Data Collection Pipeline...")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    all_data = []
    
    # 1. Google Play Store
    try:
        print("\n--- 1. Fetching Google Play Reviews ---")
        df_gp = scrape_google_play_reviews(count=3000)
        if not df_gp.empty:
            all_data.append(df_gp)
    except Exception as e:
        print(f"Failed to fetch Google Play: {e}")
        
    # 2. Apple App Store
    try:
        print("\n--- 2. Fetching Apple App Store Reviews ---")
        df_ios = scrape_apple_app_store_reviews()
        if not df_ios.empty:
            all_data.append(df_ios)
    except Exception as e:
        print(f"Failed to fetch Apple App Store: {e}")
        
    # 3. Reddit API
    try:
        print("\n--- 3. Fetching Reddit Discussions ---")
        # limit_per_sub limits the number of threads per keyword per subreddit
        df_reddit = scrape_reddit_discussions(limit_per_sub=10)
        if not df_reddit.empty:
            all_data.append(df_reddit)
    except Exception as e:
        print(f"Failed to fetch Reddit: {e}")
        
    # 4. Web, Social & Forums (DDGS Keyless)
    try:
        print("\n--- 4. Fetching Web & Social Discussions ---")
        df_web = scrape_web_and_social(max_results=10)
        if not df_web.empty:
            all_data.append(df_web)
    except Exception as e:
        print(f"Failed to fetch Web & Social: {e}")
        
    # Combine and save
    if not all_data:
        print("\n[!] No data was collected from any source. Pipeline aborted.")
        return
        
    print("\n--- 5. Unifying Data ---")
    master_df = pd.concat(all_data, ignore_index=True)
    
    # Standardize columns just in case
    expected_cols = ['source', 'date', 'rating', 'text', 'url']
    for col in expected_cols:
        if col not in master_df.columns:
            master_df[col] = None
            
    master_df = master_df[expected_cols]
    
    print(f"Unified dataset contains {len(master_df)} raw records.")
    
    # Light deduplication (heavy cleaning happens in phase 3)
    master_df = master_df.drop_duplicates(subset=['text', 'source'])
    print(f"After dropping exact duplicates within sources, {len(master_df)} records remain.")
    
    # Save to standard path
    output_path = os.path.join('data', 'reviews_raw.csv')
    
    if os.path.exists(output_path):
        print("\n--- 6. Merging with Historical Data ---")
        try:
            historical_df = pd.read_csv(output_path)
            print(f"Loaded {len(historical_df)} historical records.")
            master_df = pd.concat([historical_df, master_df], ignore_index=True)
            master_df = master_df.drop_duplicates(subset=['text', 'source'], keep='last')
            print(f"After merging and deduplicating, total dataset size is {len(master_df)} records.")
        except Exception as e:
            print(f"Failed to load historical data: {e}")
            
    master_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n[{datetime.now()}] ✅ Data collection complete! Saved to {output_path}")
    print("\nSummary of Sources:")
    print(master_df['source'].value_counts())

if __name__ == "__main__":
    run_all_collectors()
