"""
نظام تسجيل أحداث منظم
- سجل عادي للـ stdout (يظهر في GitHub Actions logs)
- سجل محفوظ في ملف data/logs/agent.log
- إرسال أخطاء حرجة لتيليغرام (اختياري)
"""

import logging
import os
import sys
import requests
from pathlib import Path
from datetime import datetime


LOGS_DIR = Path(__file__).parent.parent / "data" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(name: str = "news_agent") -> logging.Logger:
    """إعداد logger موحد للمشروع"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # stdout للـ GitHub Actions
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # ملف log محلي
    log_file = LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def notify_telegram_admin(message: str, level: str = "info"):
    """
    إرسال إشعار لمدير النظام عبر تيليغرام
    يحتاج: TELEGRAM_ADMIN_BOT_TOKEN و TELEGRAM_ADMIN_CHAT_ID في متغيرات البيئة
    """
    token = os.getenv("TELEGRAM_ADMIN_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
    if not token or not chat_id:
        return  # غير مفعّل

    icons = {"info": "ℹ️", "warning": "⚠️", "error": "🚨", "success": "✅"}
    icon = icons.get(level, "📌")

    text = f"{icon} *وكيل الأخبار*\n\n{message}\n\n_{datetime.now().isoformat()}_"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception:
        pass  # لا نريد فشل الإشعار يكسر السكربت
