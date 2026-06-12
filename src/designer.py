"""
تصميم صور الأخبار باستخدام Pillow

يدعم:
- قوالب مخصصة لكل صفحة (PNG/JPG)
- نص عربي بشكل صحيح (RTL + reshaping)
- تخصيص موضع النص ولونه وحجمه من ملف الإعدادات
"""

from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path


def create_news_image(
    template_path: str,
    title: str,
    subtitle: str,
    output_path: str,
    font_path: str,
    design: dict = None,
):
    """
    إنشاء صورة خبر باستخدام قالب وإضافة نص عربي عليه

    Args:
        template_path: مسار قالب الصورة (إطار الصفحة الخاص)
        title: العنوان الرئيسي
        subtitle: العنوان الفرعي
        output_path: مسار حفظ الصورة الناتجة
        font_path: مسار الخط العربي (.ttf)
        design: إعدادات التصميم {
            "title_position": [x, y],
            "title_size": 60,
            "title_color": "#FFFFFF",
            "subtitle_position": [x, y],
            "subtitle_size": 36,
            "subtitle_color": "#FFD700",
            "title_max_width": 900,
            "title_align": "center"
        }
    """
    design = design or {}

    # افتراضيات للتصميم
    title_pos = tuple(design.get("title_position", [540, 540]))
    title_size = design.get("title_size", 60)
    title_color = design.get("title_color", "#FFFFFF")
    title_max_width = design.get("title_max_width", 900)
    title_align = design.get("title_align", "center")

    subtitle_pos = tuple(design.get("subtitle_position", [540, 680]))
    subtitle_size = design.get("subtitle_size", 36)
    subtitle_color = design.get("subtitle_color", "#FFD700")

    # فتح القالب
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # تحميل الخطوط
    if not Path(font_path).exists():
        raise FileNotFoundError(
            f"الخط العربي غير موجود: {font_path}\n"
            f"حمّل خط عربي مثل Cairo أو Tajawal واحفظه في fonts/arabic.ttf"
        )

    title_font = ImageFont.truetype(font_path, title_size)
    subtitle_font = ImageFont.truetype(font_path, subtitle_size)

    # تجهيز النص العربي (reshaping + bidi)
    title_shaped = _prepare_arabic_text(title)
    subtitle_shaped = _prepare_arabic_text(subtitle)

    # تقسيم العنوان لأسطر متعددة إذا كان طويلاً
    title_lines = _wrap_text(title_shaped, title_font, title_max_width, draw)

    # رسم العنوان
    line_spacing = int(title_size * 1.3)
    total_title_height = len(title_lines) * line_spacing
    start_y = title_pos[1] - total_title_height // 2

    for i, line in enumerate(title_lines):
        y = start_y + i * line_spacing
        _draw_text_with_align(
            draw, line, (title_pos[0], y), title_font, title_color, title_align
        )

    # رسم العنوان الفرعي
    if subtitle_shaped:
        _draw_text_with_align(
            draw, subtitle_shaped, subtitle_pos, subtitle_font, subtitle_color, "center"
        )

    # حفظ الصورة
    img.convert("RGB").save(output_path, "PNG", quality=95)


def _prepare_arabic_text(text: str) -> str:
    """تهيئة النص العربي للعرض الصحيح"""
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def _wrap_text(text: str, font, max_width: int, draw) -> list:
    """تقسيم النص لأسطر بحيث لا يتجاوز كل سطر max_width"""
    words = text.split(" ")
    lines = []
    current = []

    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines


def _draw_text_with_align(draw, text: str, position: tuple, font, color: str, align: str):
    """رسم نص مع محاذاة محددة (center, right, left)"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    x, y = position
    if align == "center":
        x = x - text_width // 2
    elif align == "right":
        x = x - text_width

    # إضافة ظل خفيف لتحسين القراءة
    shadow_offset = 2
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill="#000000AA")
    draw.text((x, y), text, font=font, fill=color)
