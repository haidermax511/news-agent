"""
وكيل الأخبار العراقية - نقطة الدخول الرئيسية (نسخة إنتاجية)

الاستخدام:
    python main.py                    # تشغيل عادي - ينشر للصفحات
    python main.py --dry-run          # اختبار - يولّد الصور بدون نشر
    python main.py --page=page_sports # تشغيل صفحة واحدة فقط
"""

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

from src.fetcher import fetch_news_for_category
from src.processor import process_news_with_ai
from src.designer import create_news_image
from src.publisher import (
    post_to_facebook,
    post_to_instagram,
    upload_image_to_facebook_unpublished,
)
from src.telegram_publisher import post_to_telegram
from src.storage import is_already_posted, mark_as_posted
from src.logger import setup_logger, notify_telegram_admin


load_dotenv()
log = setup_logger()

ROOT = Path(__file__).parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "templates"
LOCK_FILE = DATA_DIR / ".lock"


def acquire_lock() -> bool:
    """منع تشغيل متزامن - لو الـ lock حديث، تخطّى"""
    if LOCK_FILE.exists():
        age = (datetime.now().timestamp() - LOCK_FILE.stat().st_mtime)
        if age < 600:  # 10 دقائق
            log.warning(f"عملية أخرى قيد التشغيل (lock عمره {int(age)} ثانية)")
            return False
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.touch()
    return True


def release_lock():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()


def load_config():
    """تحميل ملفات الإعدادات"""
    pages_file = CONFIG_DIR / "pages.json"
    sources_file = CONFIG_DIR / "sources.json"

    if not pages_file.exists():
        raise FileNotFoundError(
            "config/pages.json غير موجود. انسخه من config/pages.json.example وعدّل القيم."
        )

    pages = json.loads(pages_file.read_text(encoding="utf-8"))
    sources = json.loads(sources_file.read_text(encoding="utf-8"))
    return pages, sources


def publish_to_all_platforms(page, image_path, caption, dry_run=False):
    """
    النشر على كل المنصات المُعرّفة لصفحة
    Returns: dict {"facebook": True/False, "instagram": ..., "telegram": ...}
    """
    results = {}

    # --- تيليغرام (الأسهل والأسرع) ---
    tg_channel = page.get("telegram_channel_id")
    tg_token_var = page.get("telegram_token_env")
    if tg_channel and tg_token_var:
        token = os.getenv(tg_token_var)
        if not token:
            log.error(f"  تيليغرام: متغير البيئة {tg_token_var} مفقود")
            results["telegram"] = False
        elif dry_run:
            log.info(f"  📋 [محاكاة] كان سينشر لـ تيليغرام: {tg_channel}")
            results["telegram"] = True
        else:
            try:
                post_to_telegram(token, tg_channel, image_path, caption)
                log.info(f"  ✅ تم النشر على تيليغرام: {tg_channel}")
                results["telegram"] = True
            except Exception as e:
                log.error(f"  ❌ فشل تيليغرام: {e}")
                results["telegram"] = False

    # --- فيسبوك ---
    fb_page_id = page.get("facebook_page_id")
    fb_token_var = page.get("facebook_token_env")
    fb_image_public_url = None

    if fb_page_id and fb_token_var and "REPLACE" not in fb_page_id:
        token = os.getenv(fb_token_var)
        if not token:
            log.error(f"  فيسبوك: متغير البيئة {fb_token_var} مفقود")
            results["facebook"] = False
        elif dry_run:
            log.info(f"  📋 [محاكاة] كان سينشر لـ فيسبوك: {fb_page_id}")
            results["facebook"] = True
        else:
            try:
                response = post_to_facebook(fb_page_id, token, image_path, caption)
                log.info(f"  ✅ تم النشر على فيسبوك: post_id={response.get('id', '?')}")
                results["facebook"] = True
            except Exception as e:
                log.error(f"  ❌ فشل فيسبوك: {e}")
                results["facebook"] = False

    # --- انستغرام (يحتاج رابط صورة عام) ---
    ig_id = page.get("instagram_account_id")
    if ig_id and fb_token_var and "REPLACE" not in ig_id:
        token = os.getenv(fb_token_var)
        if not token:
            log.error(f"  انستغرام: توكن مفقود")
            results["instagram"] = False
        elif dry_run:
            log.info(f"  📋 [محاكاة] كان سينشر لـ انستغرام: {ig_id}")
            results["instagram"] = True
        else:
            try:
                # نرفع الصورة لفيسبوك بدون نشرها للحصول على رابطها العام
                if not fb_image_public_url and fb_page_id:
                    fb_image_public_url = upload_image_to_facebook_unpublished(
                        fb_page_id, token, image_path
                    )

                if not fb_image_public_url:
                    log.error("  ❌ فشل الحصول على رابط الصورة العام لانستغرام")
                    results["instagram"] = False
                else:
                    response = post_to_instagram(
                        ig_id, token, fb_image_public_url, caption
                    )
                    log.info(f"  ✅ تم النشر على انستغرام: post_id={response.get('id', '?')}")
                    results["instagram"] = True
            except Exception as e:
                log.error(f"  ❌ فشل انستغرام: {e}")
                results["instagram"] = False

    return results


def process_page(page_config, sources, dry_run=False):
    """معالجة صفحة واحدة من البداية للنهاية"""
    page_name = page_config["name"]
    display_name = page_config.get("display_name", page_name)
    category = page_config["category"]

    log.info(f"\n{'═' * 50}")
    log.info(f"📄 {display_name} ({category})")
    log.info(f"{'═' * 50}")

    # 1. جلب الأخبار
    category_sources = sources.get(category, [])
    if not category_sources:
        log.warning(f"لا توجد مصادر للتصنيف: {category}")
        return False

    news_items = fetch_news_for_category(category_sources, limit=15)
    log.info(f"📰 جُلبت {len(news_items)} أخبار")

    if not news_items:
        log.warning(f"لا توجد أخبار حديثة")
        return False

    # 2. اختيار أول خبر غير منشور
    selected = next(
        (item for item in news_items if not is_already_posted(item["link"], page_name)),
        None,
    )

    if not selected:
        log.info(f"✓ كل الأخبار الجديدة سبق نشرها")
        return False

    log.info(f"📌 المختار: {selected['title'][:70]}...")
    log.info(f"   المصدر: {selected['source']}")

    # 3. معالجة بالذكاء الاصطناعي
    try:
        processed = process_news_with_ai(
            title=selected["title"],
            summary=selected.get("summary", ""),
            category=category,
        )
        log.info(f"🤖 تمت الصياغة")
    except Exception as e:
        log.error(f"فشلت المعالجة بالذكاء الاصطناعي: {e}")
        notify_telegram_admin(
            f"فشلت معالجة Gemini لصفحة {display_name}:\n{str(e)[:200]}",
            level="error",
        )
        return False

    # 4. تصميم الصورة
    template_path = TEMPLATES_DIR / page_config["template"]
    if not template_path.exists():
        log.error(f"قالب التصميم مفقود: {template_path}")
        return False

    output_image = DATA_DIR / f"{page_name}_latest.png"
    output_image.parent.mkdir(parents=True, exist_ok=True)

    try:
        create_news_image(
            template_path=str(template_path),
            title=processed["title"],
            subtitle=processed.get("subtitle", ""),
            output_path=str(output_image),
            font_path=str(ROOT / "fonts" / "arabic.ttf"),
            design=page_config.get("design", {}),
        )
        log.info(f"🎨 تم تصميم الصورة")
    except Exception as e:
        log.error(f"فشل تصميم الصورة: {e}")
        traceback.print_exc()
        return False

    # 5. النشر
    caption = processed["caption"]
    if page_config.get("append_source"):
        caption += f"\n\n📡 المصدر: {selected['source']}"

    results = publish_to_all_platforms(page_config, str(output_image), caption, dry_run=dry_run)
    success = any(results.values())

    # 6. تسجيل
    if success and not dry_run:
        mark_as_posted(selected["link"], page_name, processed["title"])
        log.info(f"📝 سُجّل في قاعدة المنشورات")

    return success


def main():
    parser = argparse.ArgumentParser(description="وكيل الأخبار العراقية")
    parser.add_argument("--dry-run", action="store_true", help="اختبار بدون نشر فعلي")
    parser.add_argument("--page", help="تشغيل صفحة محددة فقط (بالاسم)")
    parser.add_argument("--no-lock", action="store_true", help="تجاوز فحص الـ lock")
    args = parser.parse_args()

    log.info("🚀 بدء تشغيل وكيل الأخبار العراقية")
    if args.dry_run:
        log.info("⚠️  وضع المحاكاة - لن يُنشر شيء فعلياً")

    if not args.no_lock and not args.dry_run:
        if not acquire_lock():
            sys.exit(0)

    try:
        pages, sources = load_config()
    except FileNotFoundError as e:
        log.error(str(e))
        release_lock()
        sys.exit(1)

    if args.page:
        pages = [p for p in pages if p["name"] == args.page]
        if not pages:
            log.error(f"لم يتم العثور على صفحة بالاسم: {args.page}")
            release_lock()
            sys.exit(1)

    results = []
    for page in pages:
        try:
            success = process_page(page, sources, dry_run=args.dry_run)
            results.append((page["name"], success))
        except KeyboardInterrupt:
            log.warning("توقف بواسطة المستخدم")
            break
        except Exception as e:
            log.error(f"خطأ غير متوقع في {page['name']}: {e}")
            traceback.print_exc()
            results.append((page["name"], False))

    log.info(f"\n{'═' * 50}")
    log.info(f"📊 الملخص: {datetime.now().isoformat()}")
    log.info(f"{'═' * 50}")
    for name, success in results:
        icon = "✅" if success else "⏭️"
        log.info(f"{icon} {name}")

    if results and not any(s for _, s in results):
        notify_telegram_admin(
            "⚠️ كل الصفحات فشلت في النشر هذه الدورة. راجع الـ logs.",
            level="warning",
        )

    release_lock()


if __name__ == "__main__":
    main()
