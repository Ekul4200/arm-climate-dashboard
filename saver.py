import gspread
from google.oauth2.service_account import Credentials

# Google Sheets connection
def connect_to_sheet(sheet_name: str, worksheet_name: str = "Sheet1"):
    scopes = scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(worksheet_name)
    return worksheet

# Save summaries to the sheet
def save_summary_to_sheet(summary, worksheet):
    row = [
        summary["id"],
        summary["original_title"],
        summary["link"],
        summary["category"],
        summary["gpt_summary"]
    ]
    worksheet.append_row(row, value_input_option="RAW")
