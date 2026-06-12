"""
سكربت التحقق من إعداد المشروع
شغّله قبل كل شيء للتأكد أن كل شي جاهز

الاستخدام:
    python verify.py              # تحقق من كل شيء
    python verify.py --rss        # تحقق من مصادر RSS فقط
    python verify.py --gemini     # تحقق من Gemini فقط
    python verify.py --pages      # تحقق من توكنات الصفحات
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def check_mark(ok: bool) -> str:
    return "✅" if ok else "❌"


def verify_dependencies() -> bool:
    """فحص أن المكتبات المطلوبة مثبتة"""
    print("\n📦 فحص المكتبات...")
    required = [
        "feedparser",
        "google.generativeai",
        "PIL",
        "requests",
        "dotenv",
        "arabic_reshaper",
        "bidi",
    ]
    all_ok = True
    for module in required:
        try:
            __import__(module)
            print(f"  {check_mark(True)} {module}")
        except ImportError:
            print(f"  {check_mark(False)} {module} (ثبّت بـ: pip install -r requirements.txt)")
            all_ok = False
    return all_ok


def verify_files() -> bool:
    """فحص ملفات المشروع الأساسية"""
    print("\n📁 فحص الملفات الأساسية...")
    files = {
        "config/pages.json": "ملف إعدادات الصفحات (انسخ من pages.json.example)",
        "config/sources.json": "ملف مصادر RSS",
        "fonts/arabic.ttf": "خط عربي - حمّل Cairo أو Tajawal من Google Fonts",
    }
    all_ok = True
    for filepath, desc in files.items():
        exists = (ROOT / filepath).exists()
        print(f"  {check_mark(exists)} {filepath} - {desc}")
        if not exists:
            all_ok = False
    return all_ok


def verify_templates() -> bool:
    """فحص قوالب التصميم"""
    print("\n🎨 فحص قوالب التصميم...")
    pages_file = ROOT / "config" / "pages.json"
    if not pages_file.exists():
        print("  ⚠️ ملف pages.json غير موجود - تخطي")
        return False

    pages = json.loads(pages_file.read_text(encoding="utf-8"))
    all_ok = True
    for page in pages:
        template = ROOT / "templates" / page["template"]
        exists = template.exists()
        print(f"  {check_mark(exists)} {page['name']}: {page['template']}")
        if not exists:
            all_ok = False
    return all_ok


def verify_rss(verbose: bool = True) -> bool:
    """فحص مصادر RSS - يحاول جلب كل feed"""
    print("\n📡 فحص مصادر RSS...")
    import feedparser

    sources_file = ROOT / "config" / "sources.json"
    if not sources_file.exists():
        print("  ❌ ملف sources.json غير موجود")
        return False

    sources_by_category = json.loads(sources_file.read_text(encoding="utf-8"))
    total = 0
    working = 0

    for category, sources in sources_by_category.items():
        if verbose:
            print(f"\n  📂 {category}:")
        for source in sources:
            total += 1
            try:
                feed = feedparser.parse(source["url"])
                count = len(feed.entries)
                if count > 0:
                    working += 1
                    if verbose:
                        print(f"    ✅ {source['name']}: {count} خبر")
                else:
                    if verbose:
                        print(f"    ⚠️  {source['name']}: لا توجد أخبار (تحقق من الرابط)")
            except Exception as e:
                if verbose:
                    print(f"    ❌ {source['name']}: {str(e)[:60]}")

    print(f"\n  📊 النتيجة: {working}/{total} مصدر يعمل")
    return working >= total // 2  # نقبل لو نصف المصادر تعمل على الأقل


def verify_gemini() -> bool:
    """فحص مفتاح Gemini API"""
    print("\n🤖 فحص Gemini API...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("  ❌ متغير البيئة GEMINI_API_KEY غير معرّف")
        print("     احصل على المفتاح من: https://aistudio.google.com/apikey")
        return False

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content("قل: مرحبا")
        if response.text:
            print(f"  ✅ Gemini يعمل - رد بنجاح")
            return True
        else:
            print(f"  ❌ Gemini رجّع رد فارغ")
            return False
    except Exception as e:
        print(f"  ❌ خطأ: {e}")
        return False


def verify_facebook_pages() -> bool:
    """فحص توكنات صفحات فيسبوك"""
    print("\n📘 فحص توكنات فيسبوك...")
    pages_file = ROOT / "config" / "pages.json"
    if not pages_file.exists():
        print("  ⚠️ ملف pages.json غير موجود - تخطي")
        return False

    import requests
    pages = json.loads(pages_file.read_text(encoding="utf-8"))
    all_ok = True

    for page in pages:
        token_var = page.get("facebook_token_env")
        page_id = page.get("facebook_page_id")
        if not token_var or not page_id or "REPLACE" in page_id:
            print(f"  ⏭️  {page['name']}: غير مُعرّف")
            continue

        token = os.getenv(token_var)
        if not token:
            print(f"  ❌ {page['name']}: التوكن {token_var} غير موجود في البيئة")
            all_ok = False
            continue

        # اختبار التوكن بطلب معلومات الصفحة
        try:
            response = requests.get(
                f"https://graph.facebook.com/v21.0/{page_id}",
                params={"fields": "name,id", "access_token": token},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {page['name']}: متصل بصفحة '{data.get('name', '?')}'")
            else:
                print(f"  ❌ {page['name']}: {response.json().get('error', {}).get('message', 'خطأ')}")
                all_ok = False
        except Exception as e:
            print(f"  ❌ {page['name']}: {e}")
            all_ok = False

    return all_ok


def verify_instagram() -> bool:
    """فحص حسابات انستغرام المربوطة"""
    print("\n📷 فحص حسابات انستغرام...")
    pages_file = ROOT / "config" / "pages.json"
    if not pages_file.exists():
        return False

    import requests
    pages = json.loads(pages_file.read_text(encoding="utf-8"))
    has_any = False
    all_ok = True

    for page in pages:
        ig_id = page.get("instagram_account_id")
        token_var = page.get("facebook_token_env")
        if not ig_id or not token_var or "REPLACE" in ig_id:
            continue

        has_any = True
        token = os.getenv(token_var)
        if not token:
            print(f"  ❌ {page['name']}: توكن مفقود")
            all_ok = False
            continue

        try:
            response = requests.get(
                f"https://graph.facebook.com/v21.0/{ig_id}",
                params={"fields": "username,id", "access_token": token},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {page['name']}: @{data.get('username', '?')}")
            else:
                print(f"  ❌ {page['name']}: {response.json().get('error', {}).get('message', 'خطأ')}")
                all_ok = False
        except Exception as e:
            print(f"  ❌ {page['name']}: {e}")
            all_ok = False

    if not has_any:
        print("  ⏭️  لا توجد حسابات انستغرام مُعرّفة")
    return all_ok if has_any else True


def verify_telegram() -> bool:
    """فحص بوتات تيليغرام (للقنوات والإشعارات الإدارية)"""
    print("\n💬 فحص تيليغرام...")
    pages_file = ROOT / "config" / "pages.json"
    if not pages_file.exists():
        return False

    from src.telegram_publisher import verify_telegram_bot, get_channel_info
    pages = json.loads(pages_file.read_text(encoding="utf-8"))

    has_any = False
    all_ok = True

    # فحص بوت الإشعارات الإدارية أولاً
    admin_token = os.getenv("TELEGRAM_ADMIN_BOT_TOKEN")
    if admin_token:
        try:
            info = verify_telegram_bot(admin_token)
            bot_name = info.get("result", {}).get("username", "?")
            print(f"  ✅ بوت الإشعارات الإدارية: @{bot_name}")
        except Exception as e:
            print(f"  ⚠️  بوت الإشعارات الإدارية: {e}")
    else:
        print("  ⏭️  بوت الإشعارات الإدارية غير مفعّل (اختياري)")

    # فحص بوت كل صفحة
    for page in pages:
        tg_channel = page.get("telegram_channel_id")
        tg_token_var = page.get("telegram_token_env")
        if not tg_channel or not tg_token_var:
            continue

        has_any = True
        token = os.getenv(tg_token_var)
        if not token:
            print(f"  ❌ {page['name']}: توكن {tg_token_var} مفقود")
            all_ok = False
            continue

        try:
            info = get_channel_info(token, tg_channel)
            title = info.get("result", {}).get("title", "?")
            print(f"  ✅ {page['name']}: قناة '{title}'")
        except Exception as e:
            print(f"  ❌ {page['name']}: {str(e)[:80]}")
            all_ok = False

    if not has_any:
        print("  ⏭️  لا توجد قنوات تيليغرام مُعرّفة")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="التحقق من إعداد المشروع")
    parser.add_argument("--rss", action="store_true", help="تحقق من RSS فقط")
    parser.add_argument("--gemini", action="store_true", help="تحقق من Gemini فقط")
    parser.add_argument("--pages", action="store_true", help="تحقق من الصفحات فقط")
    parser.add_argument("--telegram", action="store_true", help="تحقق من تيليغرام فقط")
    parser.add_argument("--quiet", action="store_true", help="عرض ملخص فقط")
    args = parser.parse_args()

    print("=" * 60)
    print("🔍 فحص شامل لإعداد وكيل الأخبار العراقية")
    print("=" * 60)

    results = {}

    if args.rss:
        results["RSS"] = verify_rss(verbose=not args.quiet)
    elif args.gemini:
        results["Gemini"] = verify_gemini()
    elif args.pages:
        results["Facebook"] = verify_facebook_pages()
        results["Instagram"] = verify_instagram()
    elif args.telegram:
        results["Telegram"] = verify_telegram()
    else:
        # فحص شامل
        results["المكتبات"] = verify_dependencies()
        results["الملفات"] = verify_files()
        results["القوالب"] = verify_templates()
        results["RSS"] = verify_rss(verbose=not args.quiet)
        results["Gemini"] = verify_gemini()
        results["Facebook"] = verify_facebook_pages()
        results["Instagram"] = verify_instagram()
        results["Telegram"] = verify_telegram()

    # ملخص
    print("\n" + "=" * 60)
    print("📊 الملخص النهائي")
    print("=" * 60)
    for name, ok in results.items():
        print(f"  {check_mark(ok)} {name}")

    failed = [n for n, ok in results.items() if not ok]
    if failed:
        print(f"\n⚠️  يجب إصلاح: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\n🎉 كل شي جاهز! يمكنك الآن تشغيل: python main.py")
        sys.exit(0)


if __name__ == "__main__":
    main()
