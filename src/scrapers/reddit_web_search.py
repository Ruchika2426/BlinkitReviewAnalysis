import pandas as pd
import datetime
import time
from ddgs import DDGS

def scrape_reddit_via_web_search(keywords=['Blinkit', 'Zepto', 'quick commerce'], max_results_per_keyword=20):
    """
    Fallback Scraper: Uses DuckDuckGo web search to find Reddit discussions about the keywords.
    It extracts the discussion text directly from the search engine snippets, bypassing Reddit's 403 blocks!
    Returns a pandas DataFrame standardized for the Blinkit Review Analyser pipeline.
    """
    print("Initializing Reddit Web-Search Fallback Scraper...")
    
    data = []
    
    try:
        with DDGS() as ddgs:
            for keyword in keywords:
                # Search specifically within reddit for the keyword
                query = f"site:reddit.com {keyword}"
                print(f"Searching web for: {query}")
                
                # Fetch results from DuckDuckGo
                results = list(ddgs.text(query, max_results=max_results_per_keyword))
                
                for res in results:
                    url = res.get('href', '')
                    title = res.get('title', '')
                    snippet = res.get('body', '')
                    
                    full_text = f"{title}\n{snippet}".strip()
                    
                    if full_text and 'reddit.com' in url:
                        data.append({
                            'source': "Reddit (Web Search Fallback)",
                            'date': datetime.datetime.now(), # DDGS doesn't always provide exact dates, use current as fallback
                            'rating': None,
                            'text': full_text,
                            'url': url
                        })
                
                # Respectful delay between keyword searches
                time.sleep(2)
                
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.drop_duplicates(subset=['url'])
            
        print(f"✅ Successfully extracted {len(df)} discussions via web search fallback.")
        return df
        
    except Exception as e:
        print(f"Error executing web search fallback: {e}")
        return pd.DataFrame(columns=['source', 'date', 'rating', 'text', 'url'])

if __name__ == "__main__":
    df = scrape_reddit_via_web_search(max_results_per_keyword=5)
    if df.empty:
        print("\nNo data fetched.")
    else:
        print("\nSample Data:")
        print(df[['source', 'text']].head())
