import os
import re
import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

SOURCE_URL = "https://sjsuparkingstatus.sjsu.edu/GarageStatus"

SERVICE_ACCOUNT_JSON = "service_account.json" 
SHEET_NAME = "Parking Data"        
WORKSHEET_NAME = "Raw"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def fetch_html(url: str) -> str:
    r = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "parking-status-research/1.0"},
        verify=False,  # TEMPORARY workaround, never figuerd out how to fix... eplanation in README.md
    )
    r.raise_for_status()
    return r.text


def extract_percent(text: str) -> int | None:
    m = re.search(r"(\d{1,3})", text)
    if not m:
        return None
    val = int(m.group(1))
    return val if 0 <= val <= 100 else None

def parse_garages(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    name_nodes = soup.select("h2.garage__name")
    if not name_nodes:
        raise RuntimeError("No garage names found. Page structure may have changed.")

    rows = []
    for name_el in name_nodes:
        garage_name = name_el.get_text(" ", strip=True)

        # Look for the fullness span between this garage name and the next name
        fullness_el = None
        for sib in name_el.next_siblings:
            # stop when we hit the next garage name
            if getattr(sib, "name", None) == "h2" and "garage__name" in (sib.get("class") or []):
                break

            if hasattr(sib, "select_one"):
                candidate = sib.select_one("span.garage__fullness")
                if candidate:
                    fullness_el = candidate
                    break

        if not fullness_el:
            # fallback: try a very local search in the immediate parent only
            parent = name_el.parent
            fullness_el = parent.select_one("span.garage__fullness") if parent else None

        percent_full = extract_percent(fullness_el.get_text(" ", strip=True)) if fullness_el else None

        rows.append({
            "garage_name": garage_name,
            "percent_full": percent_full,
        })

    return rows

def open_sheet():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_JSON, scopes=SCOPES)
    gc = gspread.authorize(creds)
    SHEET_URL = os.environ.get("SHEET_URL")
    sh = gc.open_by_url(SHEET_URL)
    
    if not SHEET_URL:
    raise ValueError("SHEET_URL environment variable is not set.")
    
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=20)
    return ws

def ensure_header(ws):
    header = [
    "collected_at_pacific",
    "garage_name",
    "percent_full",
]

    existing = ws.row_values(1)
    if existing != header:
        if not existing:
            ws.append_row(header, value_input_option="RAW")
        else:
            ws.append_row(["NOTE: header mismatch detected; expected:"] + header, value_input_option="RAW")
    return header

def append_snapshot(ws):
    html = fetch_html(SOURCE_URL)
    garages = parse_garages(html)

    pacific = ZoneInfo("America/Los_Angeles")
    collected_at = datetime.now(pacific).isoformat()

    values = []
    for g in garages:
        values.append([
            collected_at,
            g["garage_name"],
            g["percent_full"],
        ])
    ws.append_rows(values, value_input_option="RAW")

def main():
    ws = open_sheet()
    ensure_header(ws)
    append_snapshot(ws)
    print("Appended snapshot successfully.")

if __name__ == "__main__":
    main()
