import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

API_VERSION = "v26.0"
PAGE_ID = os.environ.get("PAGE_ID")
TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

CATEGORIES = {
    "local": ("إربد", "📍 أخبار إربد"),
    "sports": ("رياضة", "⚽ الرياضة"),
    "economy": ("اقتصاد", "💰 الاقتصاد"),
    "tourism": ("سياحة", "🏞️ السياحة"),
    "community": ("مجتمع", "🤝 المجتمع"),
}

if len(sys.argv) != 2 or sys.argv[1] not in CATEGORIES:
    raise SystemExit("استخدم: local أو sports أو economy أو tourism أو community")

kind = sys.argv[1]
category, heading = CATEGORIES[kind]

with open("news.json", encoding="utf-8") as file:
    data = json.load(file)

if kind == "local":
    items = [
        item for item in data.get("news", [])
        if item.get("region") == "إربد"
        and item.get("title")
        and item.get("link")
    ]
else:
    items = [
        item for item in data.get("news", [])
        if item.get("category") == category
        and item.get("title")
        and item.get("link")
    ]

items.sort(key=lambda x: x.get("published", ""), reverse=True)

if kind == "local":
    items = [x for x in items if x.get("region") == "إربد"]

if not items:
    raise SystemExit("لا يوجد خبر متاح لهذا القسم حالياً")

item = items[0]

message = "\n".join([
    f"{heading} | شملت",
    "",
    item["title"].strip(),
    "",
    f"📍 {item.get('region', 'الأردن')}",
    f"المصدر: {item.get('source', 'المصدر الأصلي')}",
    "",
    "تابعوا شملت لأخبار إربد والأردن 🇯🇴",
    item["link"].strip()
])

print("مسودة المنشور:\n")
print(message)

if os.environ.get("PUBLISH_TO_FACEBOOK") != "1":
    print("\nوضع تجربة فقط: لم يتم النشر.")
    raise SystemExit(0)

if not PAGE_ID or not TOKEN:
    raise SystemExit("بيانات صفحة فيسبوك غير موجودة")

url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/feed"

payload = urllib.parse.urlencode({
    "message": message,
    "access_token": TOKEN
}).encode()

request = urllib.request.Request(url, data=payload, method="POST")

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode())
except urllib.error.HTTPError as error:
    print("Facebook HTTP Error:", error.code)
    print(error.read().decode("utf-8", errors="replace"))
    raise SystemExit(1)

if "id" not in result:
    raise SystemExit(f"فشل النشر: {result}")

print("تم النشر بنجاح:", result["id"])
