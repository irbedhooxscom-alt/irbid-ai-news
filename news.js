
(() => {
  "use strict";

  const NEWS_URL =
    "https://raw.githubusercontent.com/irbedhooxscom-alt/irbid-ai-news/main/news.json";

  const track = document.querySelector(".si-breaking-track");
  if (!track) return;

  async function loadNews() {
    try {
      const response = await fetch(
        NEWS_URL + "?t=" + Date.now(),
        { cache: "no-store" }
      );

      if (!response.ok) throw new Error("News unavailable");

      const data = await response.json();
      const news = (data.news || []).slice(0, 30);

      track.replaceChildren();

      if (!news.length) {
        track.textContent = "لا توجد أخبار جديدة حالياً";
        return;
      }

      const style = document.createElement("style");
      style.textContent = `
        .si-news-line {
          display: inline-flex;
          align-items: center;
          gap: 35px;
          white-space: nowrap;
          width: max-content;
          animation: siNewsMove 100s linear infinite;
        }
        .si-news-line:hover { animation-play-state: paused; }
        .si-news-line a {
          color: #fff;
          text-decoration: none;
        }
        .si-news-line a:hover { color: #d4af37; }
        .si-news-item::before {
          content: "✦";
          color: #d4af37;
          margin-left: 10px;
        }
        @keyframes siNewsMove {
          from { transform: translateX(0); }
          to { transform: translateX(50%); }
        }
      `;

      if (!document.getElementById("si-news-style")) {
        style.id = "si-news-style";
        document.head.appendChild(style);
      }

      const line = document.createElement("div");
      line.className = "si-news-line";

      news.forEach(item => {
        const link = document.createElement("a");
        link.className = "si-news-item";
        link.textContent =
          (item.category || "الأردن") + ": " + item.title;
        link.href = item.link;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        line.appendChild(link);
      });

      track.appendChild(line);

      console.log("Irbid news loaded:", news.length);

    } catch (error) {
      console.error("Irbid news:", error);
      track.textContent = "تعذر تحميل الأخبار حالياً";
    }
  }

  loadNews();
  setInterval(loadNews, 60 * 60 * 1000);
})();
