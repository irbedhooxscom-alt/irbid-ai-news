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
    ("أخبار إربد اليوم", "local"),
    ("أخبار محافظة إربد والرمثا", "local"),
    ("بلديات إربد والخدمات", "local"),
    ("جامعة اليرموك وجامعة العلوم والتكنولوجيا", "local"),
    ("أخبار الأردن اليوم وقرارات الحكومة", "national"),
    ("الأردن اقتصاد وأسعار وقرارات اقتصادية", "national"),
    ("الدوري الأردني كرة القدم الحسين إربد", "national"),
    ("رياضة الأردن المنتخب الأردني", "national"),
    ("السياحة في الأردن والمواقع السياحية", "national"),
    ("سياحة إربد والأماكن السياحية", "local"),
    ("مجتمع الأردن مبادرات وأخبار إنسانية", "national"),
    ("أخبار المجتمع في إربد ومبادرات", "local"),
    ("الأردن تعليم وصحة وخدمات", "national"),
]

TOPICS = {
    "رياضة": [
        "مباراة", "الدوري", "كرة القدم", "المنتخب", "رياضة",
        "الحسين إربد", "الفيصلي", "الوحدات", "الرمثا الرياضي",
        "بطولة", "هدف", "لاعب", "مدرب"
    ],
    "اقتصاد": [
        "اقتصاد", "اقتصادي", "أسعار", "السوق", "الدينار",
        "الذهب", "النفط", "الضريبة", "الاستثمار", "التجارة",
        "الرواتب", "البطالة", "الوظائف", "بنك"
    ],
    "سياحة": [
        "سياحة", "سياحي", "سياحية", "آثار", "موقع أثري",
        "محمية", "زوار", "سياح", "رحلات", "مهرجان"
    ],
    "مجتمع": [
        "مجتمع", "مبادرة", "حملة", "تبرع", "متطوع",
        "وفاة", "وفاة", "تهنئة", "تكريم", "طلاب",
        "مدارس", "جامعة", "صحة", "مستشفى"
    ]
}

def clean_text(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", value).strip()

def classify_region(text, search_type):
    if any(term.casefold() in text for term in LOCAL_TERMS):
        return "إربد"
    return "الأردن"

def classify_topic(title, description):
    text = (title + " " + description).casefold()

    for category, keywords in TOPICS.items():
        if any(word.casefold() in text for word in keywords):
            return category

    return "أخبار عامة"

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
                description = clean_text(item.findtext("description", ""))
                pub_date = item.findtext("pubDate", "").strip()

                if not title or not link:
                    continue

                key = re.sub(r"\W+", "", title.casefold())
                if key in seen:
                    continue

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

                seen.add(key)

                source_node = item.find("source")
                source = (
                    clean_text(source_node.text)
                    if source_node is not None and source_node.text
                    else "Google News"
                )

                full_text = (title + " " + description).casefold()

                results.append({
                    "title": title,
                    "description": description,
                    "link": link,
                    "published": published,
                    "region": classify_region(full_text, search_type),
                    "category": classify_topic(title, description),
                    "source": source
                })

        except Exception as error:
            print("Feed error:", term, error)

    results.sort(key=lambda item: item["published"], reverse=True)

    data = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "news": results[:200]
    }

    with open("news.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print("News updated:", len(results))

    for category in ["إربد", "الأردن"]:
        print(category + ":", sum(x["region"] == category for x in results))

    for category in ["رياضة", "اقتصاد", "سياحة", "مجتمع", "أخبار عامة"]:
        print(category + ":", sum(x["category"] == category for x in results))

if __name__ == "__main__":
    get_news()
