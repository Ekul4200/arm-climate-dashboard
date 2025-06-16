import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import re
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from google.oauth2.service_account import Credentials
import gspread
import json
from openai import OpenAI

# --- Setup ---

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client_gsheet = gspread.authorize(creds)

SHEET_NAME = "Monthly Climate Summaries"
worksheet = client_gsheet.open(SHEET_NAME).sheet1
rows = worksheet.get_all_values()
headers = rows[0]
data = rows[1:]
df = pd.DataFrame(data, columns=headers)

# --- Data Parsing ---
def extract_month(summary_text):
    try:
        if "Relevance to Arm:" in summary_text:
            return datetime.now().strftime("%B %Y")
    except:
        pass
    return "Unknown"

def extract_relevance(summary_text):
    match = re.search(r"Relevance to Arm:\s*(High|Medium|Low)", summary_text)
    return match.group(1) if match else "Unknown"

def extract_mentions(summary):
    match = re.search(r"(Company|Competitor|Industry)[^\n:]*: (.+)", summary)
    if match:
        mentions = [c.strip() for c in match.group(2).split(",")]
        return [m for m in mentions if m.lower() not in ("n/a", "none", "", "unknown")]
    return []

def extract_themes(summary):
    lines = summary.splitlines()
    keywords = []
    for line in lines:
        if any(term in line.lower() for term in ["net zero", "scope", "emission", "datacenter", "energy", "regulation", "supply chain", "ai"]):
            words = re.findall(r"\b[a-zA-Z]{4,}\b", line)
            keywords.extend([w.lower() for w in words if w.lower() not in ENGLISH_STOP_WORDS])
    return keywords

df["Month"] = df["gpt_summary"].apply(extract_month)
df["Relevance"] = df["gpt_summary"].apply(extract_relevance)
df["Themes"] = df["gpt_summary"].apply(extract_themes)

# --- UI ---
st.title("🌍 Arm Climate Trends Dashboard")
st.markdown(f"⏱ Last updated: **{datetime.now().strftime('%d %B %Y')}**")

available_months = sorted(df["Month"].unique(), reverse=True)
selected_month = st.selectbox("📅 View month:", available_months)
df_filtered = df[df["Month"] == selected_month]

categories = df_filtered["category"].unique()
selected_categories = st.multiselect("📂 Filter by category:", categories, default=list(categories))
relevance_options = ["High", "Medium"]
selected_relevance = st.multiselect("📊 Show relevance:", relevance_options, default=relevance_options)

def relevance_filter(summary):
    for r in selected_relevance:
        if f"Relevance to Arm: {r}" in summary:
            return True
    return False

df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]
df_filtered = df_filtered[df_filtered["gpt_summary"].apply(relevance_filter)]

# --- GPT Monthly Overview ---
st.markdown("## 🧠 What to Know This Month")
try:
    top_summaries = "\n\n".join(df_filtered["gpt_summary"].head(10).tolist())
    overview_prompt = f"""
You are a sustainability strategy analyst at a semiconductor company (Arm).
Based on the summaries below, extract the **5 most important insights or trends** from this month's climate-related activity.
Each insight should be 1 bullet point and include relevant company names, themes (e.g. Scope 3, regulation, datacenter energy), or changes in the policy landscape.

Summaries:
{top_summaries}

Return exactly 5 bullet points.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": overview_prompt}],
        temperature=0.4
    )
    st.markdown(response.choices[0].message.content.strip())
except Exception as e:
    st.warning(f"⚠️ Could not generate overview: {e}")

# --- Monthly Stats ---
st.markdown("## 📊 Monthly Stats & Mentions")

total = len(df_filtered)
high_relevance = len(df_filtered[df_filtered["Relevance"] == "High"])

mention_list = df_filtered["gpt_summary"].apply(extract_mentions).sum()
top_mentions = Counter(mention_list).most_common(5)

st.markdown(f"- 🔢 Total summaries: **{total}**")
st.markdown(f"- 🎯 High relevance to Arm: **{high_relevance}**")
st.markdown("- 🏢 Top Industry Mentions:")
for name, count in top_mentions:
    st.markdown(f"  - {name} ({count} mentions)")

# --- Theme Trend Chart ---
st.markdown("## 📈 Trending Topics This Month")

theme_list = df_filtered["Themes"].sum()
top_themes = Counter(theme_list).most_common(10)
theme_df = pd.DataFrame(top_themes, columns=["Theme", "Count"])

fig = px.bar(
    theme_df,
    x="Theme",
    y="Count",
    title="Top Themes in Article Summaries",
    color="Theme",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# --- Spotlight Panel ---
st.markdown("## 🎯 High-Relevance Spotlight (Top 10 Only)")

spotlight = df_filtered[df_filtered["Relevance"] == "High"].head(10)
if spotlight.empty:
    st.info("No high-relevance articles found for this month.")
else:
    for _, row in spotlight.iterrows():
        st.markdown("----")
        st.markdown(f"🟢 **{row['original_title']}**")
        st.markdown(f"📎 [Link to article]({row['link']})")
        st.markdown(f"🏷️ Category: `{row['category']}`")
        st.markdown(f"📝 {row['gpt_summary'].split('Summary:', 1)[-1].strip()}")

# --- Full Article List ---
st.markdown("## 📚 All Filtered Summaries")
for _, row in df_filtered.iterrows():
    st.markdown("----")
    st.subheader(row["original_title"])
    st.markdown(f"📎 [Link to article]({row['link']})")
    st.markdown(f"🏷️ Category: `{row['category']}`")
    st.markdown(f"📝 {row['gpt_summary']}")

# --- CSV Download ---
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download this month's summaries (CSV)", csv, file_name=f"{selected_month}_summaries.csv")
