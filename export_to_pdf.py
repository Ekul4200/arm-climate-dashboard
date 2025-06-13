import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from weasyprint import HTML
import os

# --- Setup Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

# Load data
SHEET_NAME = "Monthly Climate Summaries"
worksheet = client.open(SHEET_NAME).sheet1
rows = worksheet.get_all_values()
headers = rows[0]
data = rows[1:]
df = pd.DataFrame(data, columns=headers)

# Filter by current month
current_month = datetime.now().strftime("%B %Y")
df["Month"] = current_month  # Simplified logic for testing

# Build HTML content
html = f"""
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; padding: 2em; }}
h1 {{ font-size: 24px; }}
h2 {{ font-size: 18px; color: #2b7a78; }}
a {{ color: #1b6ca8; text-decoration: none; }}
.article {{ margin-bottom: 2em; border-bottom: 1px solid #ccc; padding-bottom: 1em; }}
</style>
</head>
<body>
<h1>Monthly Briefing – {current_month}</h1>
<p>Total summaries: {len(df)}</p>
"""

for _, row in df.iterrows():
    html += f"""
    <div class="article">
        <h2>{row['original_title']}</h2>
        <p><strong>Category:</strong> {row['category']}</p>
        <p>{row['gpt_summary'].replace('\n', '<br>')}</p>
        <p><a href="{row['link']}" target="_blank">🔗 Read original article</a></p>
    </div>
    """

html += "</body></html>"

# Save PDF
output_path = f"monthly_brief_{current_month.replace(' ', '_')}.pdf"
HTML(string=html).write_pdf(output_path)

print(f"✅ PDF created: {output_path}")
