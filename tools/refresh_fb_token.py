"""
أداة لتجديد توكنات فيسبوك (التي تنتهي بعد 60 يوم)

الاستخدام:
1. احصل على Short-Lived User Token من Graph API Explorer
2. ضع APP_ID و APP_SECRET في .env
3. شغّل: python tools/refresh_fb_token.py SHORT_LIVED_TOKEN PAGE_ID
"""

import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")


def short_to_long_user_token(short_token: str, app_id: str, app_secret: str) -> str:
    """تحويل توكن مستخدم قصير (ساعة) إلى طويل (60 يوم)"""
    response = requests.get(
        "https://graph.facebook.com/v21.0/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        },
        timeout=10,
    )
    if response.status_code != 200:
        raise RuntimeError(f"فشل تحويل التوكن: {response.text}")
    return response.json()["access_token"]


def get_page_token(long_user_token: str, page_id: str) -> str:
    """جلب Page Access Token طويل العمر من User Token طويل"""
    response = requests.get(
        f"https://graph.facebook.com/v21.0/{page_id}",
        params={
            "fields": "access_token",
            "access_token": long_user_token,
        },
        timeout=10,
    )
    if response.status_code != 200:
        raise RuntimeError(f"فشل جلب توكن الصفحة: {response.text}")
    data = response.json()
    if "access_token" not in data:
        raise RuntimeError(f"لم يتم إرجاع توكن صفحة: {data}")
    return data["access_token"]


def check_token_validity(token: str) -> dict:
    """فحص صلاحية توكن - يرجّع معلومات المالك والصلاحيات"""
    response = requests.get(
        "https://graph.facebook.com/v21.0/me/permissions",
        params={"access_token": token},
        timeout=10,
    )
    return response.json()


def main():
    if len(sys.argv) < 3:
        print("""
الاستخدام:
    python tools/refresh_fb_token.py <SHORT_LIVED_USER_TOKEN> <PAGE_ID>

خطوات الحصول على التوكن:
1. ادخل https://developers.facebook.com/tools/explorer/
2. اختر تطبيقك من القائمة العلوية
3. اضغط "Get User Access Token" واطلب الصلاحيات:
   - pages_show_list
   - pages_read_engagement
   - pages_manage_posts
   - instagram_basic
   - instagram_content_publish
4. انسخ التوكن
5. شغّل هذا السكربت

متطلبات في .env:
    FB_APP_ID=...
    FB_APP_SECRET=...
""")
        sys.exit(1)

    short_token = sys.argv[1]
    page_id = sys.argv[2]
    app_id = os.getenv("FB_APP_ID")
    app_secret = os.getenv("FB_APP_SECRET")

    if not app_id or not app_secret:
        print("❌ ضع FB_APP_ID و FB_APP_SECRET في ملف .env")
        sys.exit(1)

    print("\n🔄 تحويل توكن المستخدم القصير إلى طويل...")
    try:
        long_user_token = short_to_long_user_token(short_token, app_id, app_secret)
        print(f"✅ تم - مدة الصلاحية: 60 يوم")
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)

    print(f"\n🔄 جلب Page Access Token للصفحة {page_id}...")
    try:
        page_token = get_page_token(long_user_token, page_id)
        print(f"✅ تم")
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🎉 Page Access Token (طويل العمر - 60 يوم):")
    print("=" * 60)
    print(page_token)
    print("=" * 60)
    print("\n💡 احفظه في GitHub Secrets باسم FB_TOKEN_PAGE_X المناسب")
    print("💡 ذكّر نفسك بتجديده كل ~55 يوم لتجنب الانقطاع")


if __name__ == "__main__":
    main()
