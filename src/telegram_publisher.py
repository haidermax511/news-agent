"""
وحدة النشر على قنوات تيليغرام
أسهل وأسرع وسيلة - تشتغل في دقائق بدون انتظار موافقات

كيف تنشئ بوت:
1. كلّم @BotFather في تيليغرام
2. أرسل /newbot واتبع التعليمات
3. احفظ التوكن الذي يعطيك إياه
4. أضف البوت كأدمن في قناتك مع صلاحية النشر
"""

import requests
from pathlib import Path


TELEGRAM_API = "https://api.telegram.org/bot{}"


def post_to_telegram(
    bot_token: str,
    channel_id: str,
    image_path: str,
    caption: str,
) -> dict:
    """
    نشر صورة مع caption على قناة تيليغرام

    Args:
        bot_token: توكن البوت من BotFather
        channel_id: معرف القناة (@channelname أو -100xxxxx)
        image_path: مسار الصورة المحلية
        caption: نص الكابشن (يدعم HTML البسيط)

    Returns:
        استجابة API
    """
    if not bot_token:
        raise ValueError("Bot token مفقود")
    if not channel_id:
        raise ValueError("Channel ID مفقود")

    url = TELEGRAM_API.format(bot_token) + "/sendPhoto"

    # تيليغرام يحدّ الكابشن بـ 1024 حرف
    if len(caption) > 1024:
        caption = caption[:1020] + "..."

    with open(image_path, "rb") as img:
        files = {"photo": img}
        data = {
            "chat_id": channel_id,
            "caption": caption,
            "parse_mode": "HTML",
        }
        response = requests.post(url, files=files, data=data, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(
            f"فشل النشر على تيليغرام ({response.status_code}): {response.text}"
        )

    return response.json()


def verify_telegram_bot(bot_token: str) -> dict:
    """التحقق من صلاحية توكن البوت"""
    url = TELEGRAM_API.format(bot_token) + "/getMe"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"توكن البوت غير صالح: {response.text}")
    return response.json()


def get_channel_info(bot_token: str, channel_id: str) -> dict:
    """جلب معلومات القناة للتحقق من وصول البوت إليها"""
    url = TELEGRAM_API.format(bot_token) + "/getChat"
    response = requests.get(url, params={"chat_id": channel_id}, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"فشل الوصول للقناة: {response.text}")
    return response.json()
