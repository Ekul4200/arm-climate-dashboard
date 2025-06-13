from news_fetcher import fetch_articles
from summarizer import summarize_article
from saver import connect_to_sheet, save_summary_to_sheet
import time

# Connect to your Google Sheet
worksheet = connect_to_sheet("Monthly Climate Summaries")

# Fetch articles
print("📡 Fetching articles...")
articles = fetch_articles()
print(f"✅ Retrieved {len(articles)} articles")

# Loop through each article and summarize
for i, article in enumerate(articles):
    print(f"\n🧠 Summarizing article {i+1}/{len(articles)}: {article['title']}")
    
    summary = summarize_article(article)

    if summary:
        print("📤 Saving summary to Google Sheet...")
        save_summary_to_sheet(summary, worksheet)
        print("✅ Saved successfully")
    else:
        print("⚠️ Skipping: GPT failed to summarize this article")

    # Pause between calls to avoid rate limits
    time.sleep(1)
