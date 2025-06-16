import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from collections import Counter

# --- Mock Data ---
data = {
    "original_title": [
        "EU Targets Scope 3 Emissions",
        "Google Announces Renewable Datacenter Initiative",
        "Microsoft Expands Carbon Removal Programs",
        "AI Models Under Scrutiny for Energy Use",
        "NVIDIA Commits to Net Zero by 2035"
    ],
    "category": ["regulations", "ai_climate", "ai_climate", "ai_climate", "ai_climate"],
    "link": [
        "https://example.com/eu-scope-3",
        "https://example.com/google-renewables",
        "https://example.com/microsoft-carbon",
        "https://example.com/ai-energy-scrutiny",
        "https://example.com/nvidia-net-zero"
    ],
    "gpt_summary": [
        "Title: EU Targets Scope 3\nSummary: New EU policy aims to enforce Scope 3 emissions tracking across tech companies.\nRelevance to Arm: High\nIndustry: EU Commission",
        "Title: Google Renewable Datacenters\nSummary: Google plans 100% renewable datacenter shift by 2030.\nRelevance to Arm: High\nIndustry: Google",
        "Title: Microsoft Carbon Program\nSummary: Microsoft boosts carbon removal, citing semiconductor supply chain impact.\nRelevance to Arm: Medium\nIndustry: Microsoft",
        "Title: AI Energy Scrutiny\nSummary: Watchdogs highlight AI model power consumption in new report.\nRelevance to Arm: Medium\nIndustry: OpenAI",
        "Title: NVIDIA Net Zero\nSummary: NVIDIA commits to full net zero roadmap.\nRelevance to Arm: High\nIndustry: NVIDIA"
    ]
}

# Convert to DataFrame
df = pd.DataFrame(data)
df["Month"] = datetime.now().strftime("%B %Y")
df["Relevance"] = df["gpt_summary"].str.extract(r"Relevance to Arm: (High|Medium|Low)")

# --- UI ---
st.title("🌍 Arm Climate Trends Dashboard (Test Mode)")
st.markdown(f"⏱ Last updated: **{datetime.now().strftime('%d %B %Y')}**")

# --- GPT Overview (Mocked for demo) ---
st.markdown("## 🧠 What to Know This Month")
st.markdown("""
- Scope 3 reporting is rising in priority across the EU
- Google and NVIDIA continue datacenter decarbonization
- Microsoft is pushing deeper into supply chain carbon removal
- Watchdogs are targeting AI energy transparency
- Net zero commitments continue to accelerate in big tech
""")

# --- Stats ---
st.markdown("## 📊 Monthly Stats")
st.markdown(f"- 🔢 Total summaries: **{len(df)}**")
st.markdown(f"- 🎯 High relevance to Arm: **{(df['Relevance'] == 'High').sum()}**")

# --- Trend Chart (by Company) ---
def extract_industry(summary):
    match = pd.Series(summary).str.extract(r"Industry:\s*(.*)")
    return match[0].str.strip()

industry_mentions = extract_industry(df["gpt_summary"])
top_industries = Counter(industry_mentions).most_common()
industry_df = pd.DataFrame(top_industries, columns=["Company", "Mentions"])

fig = px.bar(industry_df, x="Company", y="Mentions", title="Industry Mentions")
st.plotly_chart(fig, use_container_width=True)

# --- Spotlight ---
st.markdown("## 🎯 High-Relevance Spotlight")
for _, row in df[df["Relevance"] == "High"].iterrows():
    st.markdown("----")
    st.subheader(row["original_title"])
    st.markdown(f"📎 [Link to article]({row['link']})")
    st.markdown(f"🏷️ Category: `{row['category']}`")
    st.markdown(f"📝 {row['gpt_summary'].split('Summary:', 1)[-1].strip()}")

# --- Download ---
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv, file_name="mock_summaries.csv")
