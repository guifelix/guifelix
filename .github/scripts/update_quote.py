import requests
import random
import json
import os
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# --- Force IPv4 (fixes DNS issues in some CI environments) ---
def force_ipv4():
    import urllib3.util.connection as urllib3_cn

    def allowed_gai_family():
        return socket.AF_INET

    urllib3_cn.allowed_gai_family = allowed_gai_family


force_ipv4()


# --- Robust session with retries ---
def create_session():
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    return session


session = create_session()


# --- APIs ---
APIS = [
    {
        "url": "https://stoic-quotes.com/api/quote",
        "parse": lambda r: (r["text"], r["author"]),
    },
    {
        "url": "https://stoic.tekloon.net/stoic-quote",
        "parse": lambda r: (r["data"]["quote"], r["data"]["author"]),
    },
]


# --- Fetch quote with fallback ---
def fetch_quote():
    random.shuffle(APIS)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for api in APIS:
        try:
            print(f"Trying API: {api['url']}")
            response = session.get(api["url"], headers=headers, timeout=5)
            response.raise_for_status()

            data = response.json()
            quote, author = api["parse"](data)

            if quote and author:
                return quote.strip(), author.strip()

        except Exception as e:
            print(f"⚠️ Failed: {api['url']} -> {e}")

    # Hard fallback (never let CI fail)
    print("⚠️ All APIs failed. Using fallback quote.")
    return (
        "Waste no more time arguing what a good man should be. Be one.",
        "Marcus Aurelius",
    )


quote, author = fetch_quote()


# --- Prepare new entry ---
new_entry = {
    "quote": quote,
    "author": author,
}


# --- GitHub Gist setup ---
gist_id = os.environ["GIST_ID"]
token = os.environ["GITHUB_TOKEN"]

gist_url = f"https://api.github.com/gists/{gist_id}"
headers = {"Authorization": f"token {token}"}


# --- Fetch current gist ---
response = session.get(gist_url, headers=headers, timeout=5)
response.raise_for_status()

gist_data = response.json()
file_name = list(gist_data["files"].keys())[0]

quotes_json = json.loads(gist_data["files"][file_name]["content"])


# --- Update if new ---
if new_entry not in quotes_json:
    quotes_json.append(new_entry)

    payload = {
        "files": {
            file_name: {
                "content": json.dumps(
                    quotes_json,
                    indent=2,
                    ensure_ascii=False
                )
            }
        }
    }

    update_response = session.patch(
        gist_url,
        headers=headers,
        json=payload,
        timeout=5
    )
    update_response.raise_for_status()

    print(f"✅ Added quote by {author}")

else:
    print("⚠️ Quote already exists — skipping.")
