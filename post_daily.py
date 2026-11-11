import json
import os
import urllib.parse
import urllib.request
import urllib.error

PAGE_ID = os.environ.get("PAGE_ID")
TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
API_VERSION = "v26.0"

with open("news.json", encoding="utf-8") as f:
    data = json.load(f)

news = data.get("news", [])

# اختيار خبر واحد من كل تصنيف، مع إعطاء الأولوية لإربد
categories = ["أخبار عامة", "رياضة", "اقتصاد", "سياحة", "مجتمع"]
selected = []
used = set()

for category in categories:
    candidates = [
        item for item in news
        if item.get("category") == category
        and item.get("link")
        and item.get("title")
    ]

    candidates.sort(
        key=lambda item: (
            item.get("region") == "إربد",
            item.get("published", "")
        ),
        reverse=True
    )

    for item in candidates:
        if item["link"] not in used:
            selected.append(item)
            used.add(item["link"])
            break

# إكمال المنشور بأخبار أخرى إذا لم تتوفر جميع التصنيفات
for item in news:
    if len(selected) >= 5:
        break
    if item.get("link") and item["link"] not in used:
        selected.append(item)
        used.add(item["link"])

if not selected:
    raise SystemExit("لا توجد أخبار صالحة للنشر")

labels = {
    "رياضة": "⚽ الرياضة",
    "اقتصاد": "💰 الاقتصاد",
    "سياحة": "🏞️ السياحة",
    "مجتمع": "🤝 المجتمع",
    "أخبار عامة": "📰 أخبار عامة"
}

lines = [
    "📰 شملت | موجز إربد والأردن",
    "",
    "أبرز المستجدات من حولكم:",
    ""
]

for item in selected:
    category = item.get("category", "أخبار عامة")
    region = item.get("region", "الأردن")
    label = labels.get(category, "📰 الأخبار")

    lines.append(f"{label} | {region}")
    lines.append(item["title"].strip())
    lines.append("🔗 " + item["link"].strip())
    lines.append("")

lines += [
    "تابعوا صفحة شملت ليصلكم كل جديد.",
    "إربد والأردن في قلب الحدث 🇯🇴"
]

message = "\n".join(lines)

print("مسودة منشور شملت:\n")
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
except urllib.error.HTTPError as e:
    print("Facebook HTTP Error:", e.code)
    print(e.read().decode("utf-8", errors="replace"))
    raise SystemExit(1)

if "id" not in result:
    raise SystemExit(f"فشل النشر: {result}")

print("تم النشر بنجاح. رقم المنشور:", result["id"])
