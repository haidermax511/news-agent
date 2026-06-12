"""
معالجة الأخبار بالذكاء الاصطناعي باستخدام Google Gemini

يقوم بـ:
- إعادة صياغة العنوان بشكل جذاب
- كتابة caption للنشر
- توليد عنوان فرعي مختصر للصورة
"""

import os
import json
import re
import google.generativeai as genai


CATEGORY_PROMPTS = {
    "general": "أخبار عامة وعاجلة من العراق",
    "politics": "أخبار سياسية وأمنية عراقية",
    "sports": "أخبار رياضية عراقية وعربية",
    "economy": "أخبار اقتصادية ومحلية عراقية",
}


def process_news_with_ai(title: str, summary: str, category: str) -> dict:
    """
    معالجة خبر بالذكاء الاصطناعي

    Returns:
        {
            "title": "العنوان المُعاد صياغته للصورة",
            "subtitle": "نص فرعي قصير للصورة",
            "caption": "نص النشر الكامل مع الهاشتاقات"
        }
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("متغير البيئة GEMINI_API_KEY غير معرّف")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    category_desc = CATEGORY_PROMPTS.get(category, "أخبار عامة")

    prompt = f"""أنت محرر أخبار محترف لصفحة عراقية متخصصة في: {category_desc}

اقرأ هذا الخبر وأعد صياغته:

العنوان الأصلي: {title}
الملخص: {summary}

المطلوب: أعد ردك بصيغة JSON فقط، بدون أي نص آخر، بهذا الشكل بالضبط:
{{
  "title": "عنوان قصير وجذاب لا يتجاوز 12 كلمة، يصلح لوضعه على صورة",
  "subtitle": "نص فرعي مختصر جداً 4-7 كلمات يلخص الفكرة",
  "caption": "نص النشر للسوشيال ميديا: ابدأ بإيموجي مناسب، ثم العنوان، ثم 2-3 أسطر تفاصيل، ثم 5-7 هاشتاقات عراقية مناسبة. الإجمالي بين 60-150 كلمة"
}}

قواعد مهمة:
- استخدم العربية الفصحى المبسطة
- تجنب أي عبارات تحريضية أو طائفية أو مسيئة
- لا تذكر مصادر غير موثقة
- لا تختلق معلومات لم ترد في الخبر الأصلي
- إذا كان الخبر يحتوي على معلومات قد تكون مضللة، صغ بحيادية"""

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # تنظيف الناتج من backticks محتملة
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```\s*$", "", raw_text)

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        # محاولة استخراج JSON من النص
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            result = json.loads(match.group(0))
        else:
            raise ValueError(f"فشل تحليل ناتج Gemini: {raw_text[:200]}")

    # تحقق من وجود الحقول المطلوبة
    for key in ("title", "subtitle", "caption"):
        if key not in result or not result[key]:
            result[key] = title if key == "title" else ""

    return result
