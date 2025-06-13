import os
from openai import OpenAI
from dotenv import load_dotenv
from news_fetcher import fetch_articles

# Load API key from .env
load_dotenv()

def summarize_article(article):
    prompt = f"""
You are a sustainability analyst at a semiconductor company (Arm) focused on climate-related reporting and strategy.

Here is an article headline and URL. Please infer as much context as possible from the title and source.

Your job is to:
1. Summarize the article in 2 sentences
2. Explain how the article relates to Arm's sustainability strategy, especially in:
   - Emissions disclosure or climate regulation
   - Scope 3 or supply chain decarbonization
   - Energy use in datacenters or AI infrastructure
   - Net zero, renewables, or fossil fuel phase-out
3. Rate its relevance to Arm (High, Medium, or Low)
4. List any major AI or tech companies mentioned (industry peers)

Title: {article['title']}
Link: {article['link']}

Return in this format:

Title: ...
Summary: ...
Relevance to Arm: High/Medium/Low
Company/Industry Mentions: ...
"""

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        result = response.choices[0].message.content.strip()
        return {
            "id": article["id"],
            "original_title": article["title"],
            "link": article["link"],
            "category": article["category"],
            "gpt_summary": result,
        }
    except Exception as e:
        print(f"⚠️ GPT error: {e}")
        return None

# Optional manual test
if __name__ == "__main__":
    print("📡 Fetching articles...")
    articles = fetch_articles()
    print(f"✅ Got {len(articles)} articles")

    if articles:
        print("🧠 Sending first article to GPT...")
        result = summarize_article(articles[0])
        if result:
            print("\n✅ GPT Summary Output:\n")
            print(result["gpt_summary"])
        else:
            print("❌ GPT failed to return a summary.")
    else:
        print("❌ No articles available.")
