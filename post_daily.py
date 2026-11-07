import json
import os
import urllib.parse
import urllib.request

PAGE_ID = os.environ.get("PAGE_ID")
TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
API_VERSION = "v26.0"

with open("news.json", encoding="utf-8") as f:
    data = json.load(f)

news = data.get("news", [])[:5]

if not news:
    raise SystemExit("لا توجد أخبار للنشر")

lines = ["📰 موجز أخبار إربد والأردن", "", "أهم الأخبار اليوم:", ""]

for i, item in enumerate(news, 1):
    title = item.get("title", "").strip()
    link = item.get("link", "").strip()
    if title and link:
        lines.append(f"{i}. {title}\n🔗 {link}\n")

lines += ["", "المصدر: Google News", "صفحة شملت"]

message = "\n".join(lines)
print("مسودة المنشور:\n")
print(message)

if os.environ.get("PUBLISH_TO_FACEBOOK") != "1":
    print("\nوضع تجربة فقط: لم يتم النشر.")
    raise SystemExit(0)

if not PAGE_ID or not TOKEN:
    raise SystemExit("بيانات الصفحة غير موجودة")

url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/feed"
payload = urllib.parse.urlencode({
    "message": message,
    "access_token": TOKEN
}).encode()

request = urllib.request.Request(url, data=payload, method="POST")

with urllib.request.urlopen(request, timeout=30) as response:
    result = json.loads(response.read().decode())

if "id" not in result:
    raise SystemExit(f"فشل النشر: {result}")

print("تم النشر بنجاح. رقم المنشور:", result["id"])
