import requests
import urllib.parse

API_URL = "https://genshin-impact.fandom.com/api.php"

query = input("Enter dialogue or phrase to search: ").strip()

params = {
    "action": "query",
    "list": "search",
    "srsearch": query,
    "format": "json",
    "srlimit": 10
}

response = requests.get(API_URL, params=params)

if response.status_code != 200:
    print("Failed to connect to the wiki.")
    exit()

data = response.json()

results = data.get("query", {}).get("search", [])

if not results:
    print("No pages found.")
else:
    print(f"\nFound {len(results)} page(s):\n")

    for i, result in enumerate(results, start=1):
        title = result["title"]

        # Convert spaces to underscores for the URL
        url_title = urllib.parse.quote(title.replace(" ", "_"))

        url = f"https://genshin-impact.fandom.com/wiki/{url_title}"

        print(f"{i}. {title}")
        print(f"   {url}\n")