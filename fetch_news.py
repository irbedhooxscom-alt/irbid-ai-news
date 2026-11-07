
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

SEARCHES = [
    "إربد الأردن",
    "أخبار إربد",
    "الأردن أخبار",
    "الأردن قرارات حكومية",
]

def get_news():
    results = []
    seen = set()

    for term in SEARCHES:
        url = (
            "https://news.google.com/rss/search?q="
            + quote(term)
            + "&hl=ar&gl=JO&ceid=JO:ar"
        )

        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                root = ET.fromstring(response.read())

            for item in root.findall(".//item"):
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                pub_date = item.findtext("pubDate", "").strip()
                description = item.findtext("description", "").strip()

                if not title or not link or link in seen:
                    continue

                seen.add(link)

                try:
                    published = parsedate_to_datetime(pub_date).isoformat()
                except Exception:
                    published = ""

                results.append({
                    "title": title,
                    "description": description,
                    "link": link,
                    "published": published,
                    "category": "إربد" if "إربد" in term else "الأردن",
                    "source": "Google News"
                })

        except Exception as error:
            print("Feed error:", term, error)

    results.sort(
        key=lambda x: x["published"],
        reverse=True
    )

    data = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "news": results[:50]
    }

    with open("news.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print("News updated:", len(results))


if __name__ == "__main__":
    get_news()
