"""
وحدة جلب الأخبار من مصادر RSS
"""

import feedparser
import requests
from typing import List, Dict
from datetime import datetime, timedelta


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "ar,en;q=0.9",
}


def fetch_news_for_category(sources: List[Dict], limit: int = 10, hours_back: int = 48) -> List[Dict]:
    """جلب أخبار من قائمة مصادر RSS"""
    all_news = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)

    for source in sources:
        source_name = source.get("name", "?")
        try:
            print(f"  📡 محاولة: {source_name}")
            response = requests.get(source["url"], headers=HEADERS, timeout=20)
            print(f"     HTTP {response.status_code}, {len(response.content)} بايت")

            if response.status_code != 200:
                print(f"     ⚠️ كود غير 200، تخطي")
                continue

            feed = feedparser.parse(response.content)
            entries_count = len(feed.entries)
            print(f"     مدخلات في الـ feed: {entries_count}")

            if entries_count == 0:
                print(f"     ⚠️ feed فاضي")
                continue

            kept = 0
            for entry in feed.entries[:20]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])

                if published and published < cutoff_time:
                    continue

                title = entry.get("title", "").strip()
                if not title:
                    continue

                summary = entry.get("summary", "") or entry.get("description", "")
                summary = _strip_html(summary)[:500]

                all_news.append({
                    "title": title,
                    "summary": summary,
                    "link": entry.get("link", ""),
                    "source": source_name,
                    "published": published.isoformat() if published else None,
                })
                kept += 1

            print(f"     ✅ احتفظت بـ: {kept}")
        except Exception as e:
            print(f"  ❌ خطأ في {source_name}: {e}")
            continue

    all_news.sort(
        key=lambda x: x.get("published") or "0000",
        reverse=True,
    )

    return all_news[:limit]


def _strip_html(text: str) -> str:
    """إزالة وسوم HTML بشكل بسيط"""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
