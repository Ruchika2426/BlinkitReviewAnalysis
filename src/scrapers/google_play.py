import pandas as pd
from google_play_scraper import reviews, Sort
import datetime

def scrape_google_play_reviews(app_id="com.grofers.customerapp", count=600):
    """
    Scrapes recent reviews from the Google Play Store for the given app ID.
    Returns a pandas DataFrame standardized for the Blinkit Review Analyser pipeline.
    """
    print(f"Scraping Google Play reviews for {app_id} (Target: {count} reviews)...")
    
    try:
        # Fetch reviews using google-play-scraper
        result, continuation_token = reviews(
            app_id,
            lang='en',          # Language
            country='in',       # Country (India)
            sort=Sort.NEWEST,   # Get the most recent reviews
            count=count         # Number of reviews to fetch
        )
        
        data = []
        for r in result:
            data.append({
                'source': 'Google Play Store',
                'date': r['at'],
                'rating': r['score'],
                'text': r['content'],
                'url': f"https://play.google.com/store/apps/details?id={app_id}&reviewId={r['reviewId']}"
            })
            
        df = pd.DataFrame(data)
        print(f"Successfully scraped {len(df)} reviews from Google Play Store.")
        return df
        
    except Exception as e:
        print(f"Error scraping Google Play Store: {e}")
        # Return an empty dataframe with the correct schema in case of failure
        return pd.DataFrame(columns=['source', 'date', 'rating', 'text', 'url'])

if __name__ == "__main__":
    # Test execution
    df = scrape_google_play_reviews(count=10)
    if not df.empty:
        print("\nSample Data:")
        print(df[['date', 'rating', 'text']].head())
