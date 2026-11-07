import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote

LOCAL_TERMS = [
    "إربد", "الرمثا", "بني عبيد", "الحصن", "الصريح",
    "كفر يوبا", "المزار الشمالي", "المزار الجنوبي",
    "الكورة", "بني كنانة", "الأغوار الشمالية",
    "الطيبة", "غرب إربد", "جامعة اليرموك",
    "جامعة العلوم والتكنولوجيا", "الحسين إربد"
]

SEARCHES = [
    ("إربد الأردن", "local"),
    ("أخبار إربد", "local"),
    ("محافظة إربد", "local"),
    ("الرمثا الأردن", "local"),
    ("بلديات إربد", "local"),
    ("الأغوار الشمالية إربد", "local"),
    ("جامعة اليرموك إربد", "local"),
    ("الأردن أخبار وقرارات حكومية", "national"),
    ("الأردن اقتصاد وقرارات", "national"),
    ("الأردن أخبار اليوم", "national"),
]

def clean_text(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", value).strip()

def classify(title, description):
    text = (title + " " + description).casefold()

    if any(term.casefold() in text for term in LOCAL_TERMS):
        return "إربد"

    return "الأردن"

def get_news():
    results = []
    seen = set()
    now = datetime.now(timezone.utc)

    for term, search_type in SEARCHES:
        url = (
            "https://news.google.com/rss/search?q="
            + quote(term)
            + "&hl=ar&gl=JO&ceid=JO:ar"
        )

        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(request, timeout=20) as response:
                root = ET.fromstring(response.read())

            for item in root.findall(".//item"):
                title = clean_text(item.findtext("title", ""))
                link = item.findtext("link", "").strip()
                description = clean_text(
                    item.findtext("description", "")
                )
                pub_date = item.findtext("pubDate", "").strip()

                if not title or not link:
                    continue

                key = re.sub(r"\W+", "", title.casefold())

                if key in seen:
                    continue

                seen.add(key)

                try:
                    published_dt = parsedate_to_datetime(pub_date)
                    if published_dt.tzinfo is None:
                        published_dt = published_dt.replace(tzinfo=timezone.utc)
                    published_dt = published_dt.astimezone(timezone.utc)
                    age = now - published_dt
                    if age < timedelta(minutes=-30) or age > timedelta(days=7):
                        continue
                    published = published_dt.isoformat()
                except Exception:
                    continue

                source_node = item.find("source")
                source = (
                    clean_text(source_node.text)
                    if source_node is not None and source_node.text
                    else "Google News"
                )

                category = classify(title, description)

                results.append({
                    "title": title,
                    "description": description,
                    "link": link,
                    "published": published,
                    "category": category,
                    "source": source
                })

        except Exception as error:
            print("Feed error:", term, error)

    results.sort(key=lambda item: item["published"], reverse=True)
    results.sort(key=lambda item: item["category"] != "إربد")

    data = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "news": results[:150]
    }

    with open("news.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print("News updated:", len(results))
    print("إربد:", sum(x["category"] == "إربد" for x in results))
    print("الأردن:", sum(x["category"] == "الأردن" for x in results))

if __name__ == "__main__":
    get_news()
