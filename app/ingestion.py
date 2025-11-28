import feedparser
from datetime import datetime
from typing import List, Dict, Optional


# 1. Define your sources
# We use RSS feeds because they are stable and don't require complex HTML scraping.
rss_sources = {
    "Reddit": 'https://www.reddit.com/r/technology/top/.rss?t=day%22"',
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/technology-lab",
    "Tom's Hardware": "https://www.tomshardware.com/feeds/all"
}

def parse_date(entry) -> str:
    """
    Helper to extract and format date from different RSS formats.
    Returns ISO format string or current time if missing.
    """
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime(*entry.published_parsed[:6]).isoformat()
    return datetime.utcnow().isoformat()

def fetch_all_news() -> List[Dict]:
    """
    Iterates through all RSS sources, fetches news, and normalizes the data.
    """
    all_articles = []
    
    for source_name, url in rss_sources.items():
        print(f"Fetching {source_name} from {url}...")
        
        try:
            feed = feedparser.parse(url)
            
            if feed.bozo: # 'bozo' is set to 1 if there was an error parsing the XML
                print(f"Possible issue parsing {source_name}: {feed.bozo_exception}")

            # Process the first 5 entries from each source to avoid spamming
            for entry in feed.entries[:5]:
                
                # Normalize the data structure
                article = {
                    "title": entry.get("title", "No Title"),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", entry.get("description", "")),
                    "source": source_name,
                    "published_at": parse_date(entry)
                }
                
                # Basic validation
                if article["url"] and article["title"]:
                    all_articles.append(article)
                    
        except Exception as e:
            print(f"Failed to fetch {source_name}: {e}")

    print(f"Successfully fetched {len(all_articles)} articles total.")
    return all_articles

# --- Test Block ---
# This allows you to run this file directly to verify it works.
if __name__ == "__main__":
    news = fetch_all_news()
    print("\n--- TEST RESULTS ---")
    for item in news:
        print(f"[{item['source']}] {item['title']}")