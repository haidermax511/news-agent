"""
سكربت لتوليد قوالب أمثلة للصفحات الأربع
يمكنك استبدال هذه القوالب بتصميماتك الخاصة من Canva لاحقاً
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


TEMPLATES = [
    {
        "name": "page1_general.png",
        "primary": "#1a1a2e",
        "accent": "#FFD700",
        "label": "URGENT NEWS",
        "label_ar": "أخبار عاجلة",
    },
    {
        "name": "page2_politics.png",
        "primary": "#0d1b2a",
        "accent": "#E63946",
        "label": "POLITICS",
        "label_ar": "السياسة",
    },
    {
        "name": "page3_sports.png",
        "primary": "#003049",
        "accent": "#00FF87",
        "label": "SPORTS",
        "label_ar": "الرياضة",
    },
    {
        "name": "page4_economy.png",
        "primary": "#2D3142",
        "accent": "#1E90FF",
        "label": "ECONOMY",
        "label_ar": "الاقتصاد",
    },
]


def create_template(filename, primary, accent, label):
    size = 1080
    img = Image.new("RGB", (size, size), primary)
    draw = ImageDraw.Draw(img)

    # تدرج لوني خفيف من الأعلى للأسفل
    for y in range(size):
        ratio = y / size
        r1, g1, b1 = int(primary[1:3], 16), int(primary[3:5], 16), int(primary[5:7], 16)
        darken = int(40 * ratio)
        color = (max(0, r1 - darken), max(0, g1 - darken), max(0, b1 - darken))
        draw.line([(0, y), (size, y)], fill=color)

    # شريط علوي بلون التمييز
    draw.rectangle([(0, 0), (size, 80)], fill=accent)

    # شريط سفلي
    draw.rectangle([(0, size - 100), (size, size)], fill=accent)

    # ليبل التصنيف في الأعلى
    try:
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except Exception:
        font_label = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font_label)
    text_w = bbox[2] - bbox[0]
    draw.text(((size - text_w) // 2, 20), label, font=font_label, fill="#FFFFFF")

    # مستطيل شبه شفاف في المنتصف لاستيعاب النص
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [(60, 380), (size - 60, size - 200)], fill=(0, 0, 0, 100)
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # خطوط زخرفية
    draw = ImageDraw.Draw(img)
    for i in range(3):
        y = 360 + i * 8
        draw.line([(100, y), (size - 100, y)], fill=accent, width=2)

    # نص "النص هنا" placeholder
    try:
        font_placeholder = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28
        )
    except Exception:
        font_placeholder = ImageFont.load_default()

    placeholder = "[ News title will appear here ]"
    bbox = draw.textbbox((0, 0), placeholder, font=font_placeholder)
    text_w = bbox[2] - bbox[0]
    draw.text(
        ((size - text_w) // 2, size // 2 - 14),
        placeholder,
        font=font_placeholder,
        fill="#888888",
    )

    # رقم/علامة الصفحة في الأسفل
    bbox = draw.textbbox((0, 0), label, font=font_label)
    text_w = bbox[2] - bbox[0]
    draw.text(
        ((size - text_w) // 2, size - 70), label, font=font_label, fill="#FFFFFF"
    )

    return img


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "templates"
    output_dir.mkdir(exist_ok=True)

    for template in TEMPLATES:
        img = create_template(
            template["name"],
            template["primary"],
            template["accent"],
            template["label"],
        )
        path = output_dir / template["name"]
        img.save(path)
        print(f"✅ تم إنشاء: {path.name}")

    print("\n💡 هذه قوالب أولية فقط — استبدلها بتصاميمك الاحترافية من Canva")
