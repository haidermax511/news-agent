"""
وحدة جلب الأخبار من مصادر RSS - النسخة النهائية
"""

import feedparser
import requests
import logging
from typing import List, Dict
from datetime import datetime, timedelta


log = logging.getLogger("news_agent")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
}

# خبر اختباري احتياطي - يُستخدم فقط لو فشلت جميع مصادر RSS
# هذا يضمن أن باقي النظام (Gemini + التصميم + النشر) يمكن اختباره
FALLBACK_NEWS = [
    {
        "title": "اختبار النظام - نظام الأخبار العراقي يعمل بنجاح",
        "summary": "هذا منشور تجريبي تلقائي للتحقق من سلامة النظام الكاملة. النظام يقوم بجلب الأخبار، معالجتها بالذكاء الاصطناعي، تصميم الصورة بإطار مخصص، ثم النشر على القنوات.",
        "link": "https://test.example.com/news/system-test",
        "source": "نظام الاختبار الداخلي",
        "published": None,
    }
]


def fetch_news_for_category(sources: List[Dict], limit: int = 10, hours_back: int = 72) -> List[Dict]:
    """
    جلب أخبار من قائمة مصادر RSS
    لو فشلت جميع المصادر، يرجع خبر اختباري للتحقق من باقي النظام
    """
    log.info(f"🔍 بدء جلب الأخبار من {len(sources)} مصدر/مصادر")
    
    if not sources:
        log.warning("⚠️ القائمة فارغة - لا توجد مصادر")
        log.info("🔄 استخدام خبر اختباري احتياطي")
        return [_make_test_news()]

    all_news = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)

    for idx, source in enumerate(sources, start=1):
        source_name = source.get("name", f"مصدر-{idx}")
        source_url = source.get("url", "")

        if not source_url:
            log.warning(f"  [{idx}] ⚠️ {source_name}: URL فارغ - تخطي")
            continue

        log.info(f"  [{idx}] 📡 محاولة جلب من: {source_name}")
        log.info(f"      URL: {source_url[:90]}")

        try:
            response = requests.get(source_url, headers=HEADERS, timeout=20)
            log.info(f"      HTTP {response.status_code} | حجم: {len(response.content)} بايت")

            if response.status_code != 200:
                log.warning(f"      ⚠️ كود غير 200، تخطي")
                continue

            if len(response.content) < 100:
                log.warning(f"      ⚠️ محتوى صغير جداً، تخطي")
                continue

            feed = feedparser.parse(response.content)
            entries_count = len(feed.entries)
            log.info(f"      📰 مدخلات في الـ feed: {entries_count}")

            if entries_count == 0:
                log.warning(f"      ⚠️ feed فارغ، تخطي")
                continue

            kept = 0
            for entry in feed.entries[:20]:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published = datetime(*entry.published_parsed[:6])
                    except (TypeError, ValueError):
                        published = None

                # نقبل الخبر لو ما عنده تاريخ، أو لو تاريخه ضمن النطاق
                if published and published < cutoff_time:
                    continue

                summary = entry.get("summary", "") or entry.get("description", "") or ""
                summary = _strip_html(summary)[:500]

                all_news.append({
                    "title": title,
                    "summary": summary,
                    "link": entry.get("link", ""),
                    "source": source_name,
                    "published": published.isoformat() if published else datetime.now().isoformat(),
                })
                kept += 1

            log.info(f"      ✅ احتفظت بـ {kept} خبر من هذا المصدر")

        except requests.Timeout:
            log.error(f"      ❌ Timeout - المصدر بطيء")
            continue
        except requests.RequestException as e:
            log.error(f"      ❌ خطأ شبكة: {str(e)[:100]}")
            continue
        except Exception as e:
            log.error(f"      ❌ خطأ غير متوقع: {type(e).__name__}: {str(e)[:100]}")
            continue

    log.info(f"🎯 إجمالي ما تم جمعه: {len(all_news)} خبر")

    if not all_news:
        log.warning("⚠️ جميع المصادر فشلت أو لا تحتوي أخبار حديثة")
        log.info("🔄 استخدام خبر اختباري للتحقق من باقي النظام")
        return [_make_test_news()]

    # ترتيب حسب الأحدث
    all_news.sort(
        key=lambda x: x.get("published") or "0000",
        reverse=True,
    )

    return all_news[:limit]


def _make_test_news() -> Dict:
    """إنشاء خبر اختباري ديناميكي بطابع زمني فريد"""
    timestamp = datetime.now().strftime("%H:%M")
    return {
        "title": f"اختبار النظام في الساعة {timestamp} - الوكيل يعمل",
        "summary": (
            "هذا منشور تلقائي للتحقق من سلامة النظام بالكامل: "
            "جلب الأخبار، المعالجة بالذكاء الاصطناعي، تصميم الصورة، "
            f"والنشر على القنوات. الوقت: {datetime.now().isoformat()}"
        ),
        "link": f"https://test.example.com/news/{int(datetime.now().timestamp())}",
        "source": "نظام الاختبار",
        "published": datetime.now().isoformat(),
    }


def _strip_html(text: str) -> str:
    """إزالة وسوم HTML بشكل بسيط"""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
