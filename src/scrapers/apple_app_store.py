import pandas as pd
import requests
import datetime
from dateutil import parser

def scrape_apple_app_store_reviews(app_id="960335206", count=500):
    """
    Scrapes recent reviews from the Apple App Store (India) via iTunes RSS Feed.
    Returns a pandas DataFrame standardized for the Blinkit Review Analyser pipeline.
    """
    print(f"Scraping Apple App Store reviews for {app_id}...")
    
    # Apple RSS feed limits pages to 50 items, max 10 pages. We'll fetch pages until we hit count.
    data = []
    page = 1
    
    try:
        while len(data) < count and page <= 10:
            url = f"https://itunes.apple.com/in/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code} for Apple App Store RSS feed.")
                break
                
            json_data = response.json()
            feed = json_data.get('feed', {})
            entries = feed.get('entry', [])
            
            # If there's only 1 entry or 0 entries, we reached the end.
            if not entries:
                break
                
            # Sometimes the first entry is metadata about the app itself rather than a review
            # We skip it if 'im:rating' is not present
            for entry in entries:
                if 'im:rating' not in entry:
                    continue
                    
                rating = int(entry['im:rating']['label'])
                text = entry['content']['label']
                # Try to parse the date, otherwise use current time as fallback
                try:
                    date = parser.parse(entry['updated']['label']).replace(tzinfo=None)
                except Exception:
                    date = datetime.datetime.now()
                
                review_id = entry['id']['label']
                
                data.append({
                    'source': 'Apple App Store',
                    'date': date,
                    'rating': rating,
                    'text': text,
                    'url': f"https://apps.apple.com/in/app/id{app_id}?action=write-review" # Standard fallback url
                })
                
                if len(data) >= count:
                    break
                    
            page += 1
            
        df = pd.DataFrame(data)
        print(f"Successfully scraped {len(df)} reviews from Apple App Store.")
        return df
        
    except Exception as e:
        print(f"Error scraping Apple App Store: {e}")
        return pd.DataFrame(columns=['source', 'date', 'rating', 'text', 'url'])

if __name__ == "__main__":
    # Test execution
    df = scrape_apple_app_store_reviews(count=20)
    if not df.empty:
        print("\nSample Data:")
        print(df[['date', 'rating', 'text']].head())
