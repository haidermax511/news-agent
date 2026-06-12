"""
وحدة تخزين سجل المنشورات لتجنب تكرار النشر
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta


DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
LOG_FILE = DATA_DIR / "posted_news.json"

# مدة الاحتفاظ بسجل الأخبار المنشورة قبل التنظيف (بالأيام)
RETENTION_DAYS = 7


def _load_log() -> dict:
    """تحميل سجل المنشورات"""
    if not LOG_FILE.exists():
        return {}
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_log(log: dict):
    """حفظ السجل بعد تنظيفه من الأخبار القديمة"""
    cleaned = _clean_old_entries(log)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)


def _clean_old_entries(log: dict) -> dict:
    """إزالة الإدخالات الأقدم من RETENTION_DAYS"""
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    cleaned = {}
    for key, value in log.items():
        try:
            posted_at = datetime.fromisoformat(value["posted_at"])
            if posted_at >= cutoff:
                cleaned[key] = value
        except (KeyError, ValueError):
            continue
    return cleaned


def _hash_key(link: str, page_name: str) -> str:
    """توليد مفتاح فريد للسجل"""
    raw = f"{page_name}::{link}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def is_already_posted(link: str, page_name: str) -> bool:
    """التحقق إن كان الخبر قد نُشر على هذه الصفحة من قبل"""
    log = _load_log()
    key = _hash_key(link, page_name)
    return key in log


def mark_as_posted(link: str, page_name: str, title: str = ""):
    """تسجيل خبر كمنشور"""
    log = _load_log()
    key = _hash_key(link, page_name)
    log[key] = {
        "link": link,
        "page": page_name,
        "title": title[:200],
        "posted_at": datetime.now().isoformat(),
    }
    _save_log(log)
