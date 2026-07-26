import pandas as pd
import datetime
import time
from ddgs import DDGS

def scrape_web_and_social(keywords=['Blinkit', 'Zepto', 'quick commerce'], max_results=10):
    """
    Scrapes third-party sites using DuckDuckGo Search (DDGS) to bypass 403 blocks.
    Requires ZERO API keys.
    Collects data from:
      1. Community forums (Quora)
      2. Social media (Twitter)
      3. Product reviews (Trustpilot, Mouthshut)
      4. Quick-commerce discussions (HackerNews, TeamBHP)
    Returns a pandas DataFrame standardized for the Blinkit Review Analyser pipeline.
    """
    print("Initializing Web, Social & Forum Scraper (Keyless Search Engine approach)...")
    
    data = []
    
    # Map our target categories to specific site searches
    sources = {
        'Community forums': ['site:quora.com'],
        'Social media conversations': ['site:twitter.com', 'site:facebook.com'],
        'Product reviews': ['site:trustpilot.com', 'site:mouthshut.com'],
        'Quick-commerce discussions': ['site:news.ycombinator.com', 'site:teambhp.com']
    }
    
    try:
        with DDGS() as ddgs:
            for category, site_queries in sources.items():
                print(f"Fetching {category}...")
                
                for site in site_queries:
                    for keyword in keywords:
                        query = f"{keyword} {site}"
                        
                        try:
                            # Fetch search snippets
                            results = list(ddgs.text(query, max_results=max_results))
                            
                            for res in results:
                                url = res.get('href', '')
                                title = res.get('title', '')
                                snippet = res.get('body', '')
                                
                                # Skip boilerplate anti-bot snippets
                                if "The site owner hides the web page description" in snippet:
                                    continue
                                    
                                full_text = f"{title}\n{snippet}".strip()
                                
                                if full_text:
                                    data.append({
                                        'source': category,
                                        'date': datetime.datetime.now(), # Search snippets lack exact timestamps
                                        'rating': None,
                                        'text': full_text,
                                        'url': url
                                    })
                                    
                        except Exception as e:
                            print(f"  [!] Search failed for {query}: {e}")
                            
                        # Delay to prevent rate limiting from DuckDuckGo
                        time.sleep(2)
                        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.drop_duplicates(subset=['url'])
            
        print(f"✅ Successfully scraped {len(df)} records across 4 categories.")
        return df
        
    except Exception as e:
        print(f"Error scraping web/forums: {e}")
        return pd.DataFrame(columns=['source', 'date', 'rating', 'text', 'url'])

if __name__ == "__main__":
    # Test execution
    df = scrape_web_and_social(keywords=['Blinkit'], max_results=3)
    if not df.empty:
        print("\nSample Data (grouped by source category):")
        print(df['source'].value_counts())
        print("\n", df[['source', 'text']].head())
    else:
        print("\nNo data fetched.")
