import requests
import yaml
from xml.etree import ElementTree as ET
from datetime import datetime
import hashlib

# Custom headers to avoid blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

# Load feeds
def load_feeds():
    with open("feeds.yaml", "r") as f:
        return yaml.safe_load(f)

# Fetch and clean articles
def fetch_articles():
    feeds = load_feeds()
    all_articles = []

    for category, urls in feeds.items():
        print(f"\n🔍 Category: {category}")
        for url in urls:
            try:
                print(f"→ Reading: {url}")
                response = requests.get(url, headers=HEADERS, timeout=10)
                root = ET.fromstring(response.content)

                for item in root.iter("item"):
                    title = item.findtext("title", default="").strip()
                    link = item.findtext("link", default="").strip()
                    description = item.findtext("description", default="").strip()
                    pub_date = item.findtext("pubDate", default="").strip()

                    # Ensure links are valid
                    if not link or "http" not in link:
                        continue
                    if not link.startswith("http"):
                        link = "https://" + link

                    uid = hashlib.md5((title + link).encode()).hexdigest()
                    article = {
                        "id": uid,
                        "title": title,
                        "link": link,
                        "summary": description[:300],
                        "category": category,
                        "published": pub_date,
                        "fetched_at": datetime.now().isoformat()
                    }
                    all_articles.append(article)

            except Exception as e:
                print(f"⚠️ Error reading {url}: {e}")

    print(f"\n✅ Total articles fetched: {len(all_articles)}")
    return all_articles

# Test preview
if __name__ == "__main__":
    articles = fetch_articles()
    print("\n📰 First article preview:\n")
    if articles:
        print(f"Title: {articles[0]['title']}")
        print(f"Link: {articles[0]['link']}")
        print(f"Category: {articles[0]['category']}")
        print(f"Summary: {articles[0]['summary']}")
    else:
        print("❌ No articles returned.")
