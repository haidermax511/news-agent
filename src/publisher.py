"""
وحدة النشر على فيسبوك وانستغرام عبر Meta Graph API

ملاحظات مهمة:
- تتطلب موافقة Meta على تطبيقك للحصول على صلاحية pages_manage_posts
- صفحة انستغرام يجب أن تكون Business/Creator ومربوطة بصفحة فيسبوك
- التوكنات يجب أن تكون Long-Lived Page Access Tokens
"""

import requests
from typing import Optional


GRAPH_API_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def post_to_facebook(
    page_id: str,
    access_token: str,
    image_path: str,
    caption: str,
) -> dict:
    """
    نشر صورة مع تعليق على صفحة فيسبوك

    Args:
        page_id: معرف صفحة فيسبوك
        access_token: Page Access Token (long-lived)
        image_path: مسار الصورة المحلية
        caption: نص التعليق

    Returns:
        استجابة API (تحتوي على post_id)
    """
    if not access_token:
        raise ValueError("Access token مفقود")

    url = f"{GRAPH_BASE}/{page_id}/photos"

    with open(image_path, "rb") as img_file:
        files = {"source": img_file}
        data = {
            "caption": caption,
            "access_token": access_token,
        }
        response = requests.post(url, files=files, data=data, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(
            f"فشل النشر على فيسبوك ({response.status_code}): {response.text}"
        )

    return response.json()


def post_to_instagram(
    ig_account_id: str,
    access_token: str,
    image_url: str,
    caption: str,
) -> dict:
    """
    نشر صورة على حساب انستغرام تجاري عبر Graph API

    ملاحظة: يحتاج رابط صورة عام (URL) - ليس ملف محلي
    يمكن استخدام imgur API أو رفع الصورة لفيسبوك أولاً والاستفادة من رابطها

    Args:
        ig_account_id: معرف حساب انستغرام التجاري
        access_token: نفس Access Token الخاص بصفحة فيسبوك المرتبطة
        image_url: رابط عام للصورة (https://...)
        caption: نص التعليق

    Returns:
        استجابة API
    """
    if not access_token:
        raise ValueError("Access token مفقود")
    if not image_url:
        raise ValueError("رابط الصورة العام مطلوب لنشر انستغرام")

    # الخطوة 1: إنشاء media container
    create_url = f"{GRAPH_BASE}/{ig_account_id}/media"
    create_data = {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    }
    create_response = requests.post(create_url, data=create_data, timeout=30)

    if create_response.status_code != 200:
        raise RuntimeError(
            f"فشل إنشاء media container ({create_response.status_code}): {create_response.text}"
        )

    container_id = create_response.json().get("id")
    if not container_id:
        raise RuntimeError(f"لم يتم إرجاع container_id: {create_response.json()}")

    # الخطوة 2: نشر container
    publish_url = f"{GRAPH_BASE}/{ig_account_id}/media_publish"
    publish_data = {
        "creation_id": container_id,
        "access_token": access_token,
    }
    publish_response = requests.post(publish_url, data=publish_data, timeout=30)

    if publish_response.status_code != 200:
        raise RuntimeError(
            f"فشل نشر media ({publish_response.status_code}): {publish_response.text}"
        )

    return publish_response.json()


def upload_image_to_facebook_unpublished(
    page_id: str, access_token: str, image_path: str
) -> Optional[str]:
    """
    رفع صورة لفيسبوك دون نشرها للاستفادة من رابطها العام
    مفيد لاستخدام نفس الصورة في انستغرام
    """
    url = f"{GRAPH_BASE}/{page_id}/photos"
    with open(image_path, "rb") as f:
        files = {"source": f}
        data = {"published": "false", "access_token": access_token}
        response = requests.post(url, files=files, data=data, timeout=60)

    if response.status_code != 200:
        return None

    photo_id = response.json().get("id")
    if not photo_id:
        return None

    # جلب رابط الصورة العام
    img_url = f"{GRAPH_BASE}/{photo_id}"
    img_response = requests.get(
        img_url, params={"fields": "images", "access_token": access_token}, timeout=30
    )
    if img_response.status_code == 200:
        images = img_response.json().get("images", [])
        if images:
            return images[0].get("source")
    return None
