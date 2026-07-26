import os
import time
import datetime
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_comments_unauth(permalink, headers):
    """
    Fetches top comments for a specific post using unauthenticated JSON.
    """
    url = f"https://old.reddit.com{permalink}.json"
    try:
        time.sleep(2) # delay to avoid rate limiting
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            comments_data = []
            if len(data) > 1 and 'data' in data[1] and 'children' in data[1]['data']:
                comments = data[1]['data']['children']
                for c in comments[:5]: # top 5 comments
                    if c['kind'] == 't1' and 'body' in c['data']:
                        body = c['data']['body']
                        if body and body not in ["[deleted]", "[removed]"]:
                            comments_data.append({
                                'date': datetime.datetime.fromtimestamp(c['data']['created_utc']),
                                'text': body,
                                'url': f"https://www.reddit.com{c['data']['permalink']}"
                            })
            return comments_data
    except Exception as e:
        print(f"Error fetching comments unauth: {e}")
    return []

def scrape_reddit_discussions(limit_per_sub=20):
    """
    Scrapes Reddit discussions and top comments using queries.
    Tries unauthenticated public JSON first, with fallbacks to old.reddit.com and delays.
    If 403 (blocked), falls back to PRAW (Official API) if keys are provided.
    """
    queries = [
        "blinkit", 
        "blinkit experience", 
        "blinkit vs zepto", 
        "blinkit quality", 
        "quick commerce india"
    ]
    
    print("Initializing Reddit Scraper...")
    data = []
    
    # 1. Try Unauthenticated public JSON approach first
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    unauth_success = False
    
    for query in queries:
        print(f"Searching public Reddit JSON for: '{query}'")
        # Try old.reddit.com which sometimes bypasses strict blocks on www.reddit.com
        url = f"https://old.reddit.com/search.json?q={query}&sort=new&limit={limit_per_sub}"
        
        try:
            time.sleep(3) # respectful delay
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                unauth_success = True
                posts = response.json().get('data', {}).get('children', [])
                for post in posts:
                    if post['kind'] == 't3': # t3 is a link/post
                        post_data = post['data']
                        full_text = f"{post_data.get('title', '')}\n{post_data.get('selftext', '')}"
                        permalink = post_data.get('permalink', '')
                        
                        data.append({
                            'source': 'Reddit (Public API - Post)',
                            'date': datetime.datetime.fromtimestamp(post_data.get('created_utc', 0)),
                            'rating': None,
                            'text': full_text,
                            'url': f"https://www.reddit.com{permalink}"
                        })
                        
                        # Fetch comments for this post
                        comments = fetch_comments_unauth(permalink, headers)
                        for c in comments:
                            data.append({
                                'source': 'Reddit (Public API - Comment)',
                                'date': c['date'],
                                'rating': None,
                                'text': c['text'],
                                'url': c['url']
                            })
                            
            elif response.status_code in [403, 429]:
                print(f"⚠️ Unauthenticated JSON blocked ({response.status_code}).")
                unauth_success = False
                break # stop trying unauth and fallback to PRAW
                
        except Exception as e:
            print(f"Unauthenticated request failed: {e}")
            unauth_success = False
            break

    # 2. Fallback to PRAW if unauth failed or blocked
    if not unauth_success or len(data) == 0:
        print("\n🔄 Switching to PRAW (Official API) Fallback...")
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ PRAW API keys not found in .env.")
            print("To fix this and use the official Reddit API:")
            print("1. Go to https://www.reddit.com/prefs/apps")
            print("2. Click 'Create App' or 'Create Another App' at the bottom.")
            print("3. Choose 'script'. Give it a name like 'BlinkitAnalyzer'.")
            print("4. Set redirect uri to 'http://localhost:8080'.")
            print("5. Copy the client ID (under the app name) and the secret.")
            print("6. Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to your .env file.")
            print("For now, returning whatever data was collected (if any).")
            
        else:
            try:
                import praw
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent='BlinkitReviewAnalyser/1.0'
                )
                
                for query in queries:
                    print(f"Searching PRAW for: '{query}'")
                    # Search across all subreddits
                    for submission in reddit.subreddit('all').search(query, limit=limit_per_sub, sort='new'):
                        full_text = f"{submission.title}\n{submission.selftext}"
                        data.append({
                            'source': 'Reddit (PRAW - Post)',
                            'date': datetime.datetime.fromtimestamp(submission.created_utc),
                            'rating': None,
                            'text': full_text,
                            'url': f"https://www.reddit.com{submission.permalink}"
                        })
                        
                        # Fetch top comments
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list()[:5]: # top 5 comments
                            if comment.body and comment.body not in ["[deleted]", "[removed]"]:
                                data.append({
                                    'source': 'Reddit (PRAW - Comment)',
                                    'date': datetime.datetime.fromtimestamp(comment.created_utc),
                                    'rating': None,
                                    'text': comment.body,
                                    'url': f"https://www.reddit.com{comment.permalink}"
                                })
            except Exception as e:
                print(f"PRAW extraction failed: {e}")

    df = pd.DataFrame(data)
    if not df.empty:
        df = df.drop_duplicates(subset=['url'])
        
    print(f"✅ Successfully extracted {len(df)} posts and comments from Reddit.")
    return df

if __name__ == "__main__":
    df = scrape_reddit_discussions(limit_per_sub=2)
    if df.empty:
        print("\nNo data fetched.")
    else:
        print("\nSample Data:")
        print(df[['source', 'date', 'text']].head())
