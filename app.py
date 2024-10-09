import os
import gspread

from google.oauth2.service_account import Credentials

SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "example-spreadsheet")
SHARE_TO_EMAIL = os.getenv("SHARE_TO_EMAIL", None)

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = Credentials.from_service_account_file(
    "credentials.json", scopes=scopes
)

gc = gspread.authorize(credentials)

try:
    sh = gc.open(SPREADSHEET_NAME)
except Exception:
    print(f"Creating new sheet: {SPREADSHEET_NAME}")
    sh = gc.create(SPREADSHEET_NAME)
    if SHARE_TO_EMAIL:
        sh.share(SHARE_TO_EMAIL, perm_type="user", role="writer")

worksheet_list = sh.worksheets()

print(worksheet_list)
