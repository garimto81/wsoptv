#!/usr/bin/env python3
"""Drive 전체 권한으로 재인증"""

import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

CREDENTIALS_FILE = Path("C:/claude/json/desktop_credentials.json")
TOKEN_FILE = Path("C:/claude/json/token_docs.json")

# 전체 Drive 스코프 포함
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",  # 전체 Drive 접근
]

print("Requesting full Drive access...")
print(f"Scopes: {SCOPES}")
print()

flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
creds = flow.run_local_server(port=0)

# Save token
token_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes),
}

with open(TOKEN_FILE, "w", encoding="utf-8") as f:
    json.dump(token_data, f, indent=2)

print(f"Token saved: {TOKEN_FILE}")
print(f"Scopes: {creds.scopes}")
