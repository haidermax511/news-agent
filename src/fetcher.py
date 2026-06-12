"""
وحدة جلب الأخبار من مصادر RSS
"""

import feedparser
import requests
import logging
from typing import List, Dict
from datetime import datetime, timedelta


log = logging.getLogger("news_agent")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "ar,en;q=0.9",
}


def fetch_news_for_category(sources: List[Dict], limit: int = 10, hours_back: int = 48) -> List[Dict]:
    """جلب أخبار من قائمة مصادر RSS"""
    log.info(f"🔍 fetch_news_for_category تم استدعاؤها بـ {len(sources)} مصدر")
    
    all_news = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)

    if not sources:
        log.warning("⚠️ القائمة فارغة - لا مصادر")
        return []

    for source in sources:
        source_name = source.get("name", "?")
        source_url = source.get("url", "")
        try:
            log.info(f"  📡 محاولة: {source_name}")
            log.info(f"     URL: {source_url[:80]}")
            
            response = requests.get(source_url, headers=HEADERS, timeout=20)
            log.info(f"     HTTP {response.status_code}, {len(response.content)} بايت")

            if response.status_code != 200:
                log.warning(f"     ⚠️ كود غير 200، تخطي")
                continue

            feed = feedparser.parse(response.content)
            entries_count = len(feed.entries)
            log.info(f"     مدخلات في الـ feed: {entries_count}")

            if entries_count == 0:
                log.warning(f"     ⚠️ feed فاضي")
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

            log.info(f"     ✅ احتفظت بـ: {kept}")
        except Exception as e:
            log.error(f"  ❌ خطأ في {source_name}: {e}")
            continue

    all_news.sort(
        key=lambda x: x.get("published") or "0000",
        reverse=True,
    )

    log.info(f"🎯 إجمالي ما تم جلبه: {len(all_news)} خبر")
    return all_news[:limit]


def _strip_html(text: str) -> str:
    """إزالة وسوم HTML بشكل بسيط"""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
