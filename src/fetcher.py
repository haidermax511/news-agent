"""
وحدة جلب الأخبار من مصادر RSS
"""

import feedparser
from typing import List, Dict
from datetime import datetime, timedelta


def fetch_news_for_category(sources: List[Dict], limit: int = 10, hours_back: int = 6) -> List[Dict]:
    """
    جلب أخبار من قائمة مصادر RSS لتصنيف معين
    
    Args:
        sources: قائمة بمصادر RSS [{"name": "...", "url": "..."}]
        limit: العدد الأقصى للأخبار المُعادة
        hours_back: جلب الأخبار من آخر X ساعة فقط
    
    Returns:
        قائمة من الأخبار مرتبة حسب الأحدث
    """
    all_news = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)

    for source in sources:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:20]:
                # محاولة قراءة وقت النشر
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])

                # تخطي الأخبار القديمة جداً (إن وُجد تاريخ)
                if published and published < cutoff_time:
                    continue

                title = entry.get("title", "").strip()
                if not title:
                    continue

                summary = entry.get("summary", "") or entry.get("description", "")
                # تنظيف بسيط للـ HTML
                summary = _strip_html(summary)[:500]

                all_news.append({
                    "title": title,
                    "summary": summary,
                    "link": entry.get("link", ""),
                    "source": source["name"],
                    "published": published.isoformat() if published else None,
                })
        except Exception as e:
            print(f"⚠️ خطأ في جلب من {source.get('name', '?')}: {e}")
            continue

    # ترتيب حسب الأحدث (الأخبار بدون تاريخ تذهب للأخير)
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
