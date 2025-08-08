import requests
import random
import json
import os

APIS = [
    {
        "url": "https://stoic-quotes.com/api/quote",
        "parse": lambda r: (r["text"], r["author"])
    },
    {
        "url": "https://stoic.tekloon.net/stoic-quote",
        "parse": lambda r: (r["data"]["quote"], r["data"]["author"])
    }
]

gist_id = os.environ["GIST_ID"]
token = os.environ["GITHUB_TOKEN"]

# Pick random API
api = random.choice(APIS)
quote, author = api["parse"](requests.get(api["url"]).json())

# Normalize for comparison
new_entry = {
    "quote": quote.strip(),
    "author": author.strip()
}

gist_url = f"https://api.github.com/gists/{gist_id}"
headers = {"Authorization": f"token {token}"}

# Fetch current gist content
gist_data = requests.get(gist_url, headers=headers).json()
file_name = list(gist_data["files"].keys())[0]
quotes_json = json.loads(gist_data["files"][file_name]["content"])

# Only add if not already present
if new_entry not in quotes_json:
    quotes_json.append(new_entry)
    payload = {
        "files": {
            file_name: {
                "content": json.dumps(quotes_json, indent=2, ensure_ascii=False)
            }
        }
    }
    requests.patch(gist_url, headers=headers, json=payload)
    print(f"✅ Added quote by {author}")
else:
    print("⚠️ Quote already exists — skipping.")
