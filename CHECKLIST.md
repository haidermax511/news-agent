# ✅ قائمة النشر السريعة (Deployment Checklist)

اطبع هذه الصفحة وضع عليها علامات بالترتيب.

## المرحلة 1: تيليغرام فقط (30 دقيقة)

### الحسابات والتوكنات
- [ ] حساب GitHub
- [ ] حساب Google (لـ Gemini)
- [ ] مفتاح Gemini API محفوظ
- [ ] أنشأت 4 بوتات تيليغرام من @BotFather
- [ ] حفظت توكنات البوتات الأربعة
- [ ] أنشأت 4 قنوات تيليغرام
- [ ] أضفت كل بوت كأدمن في قناته
- [ ] أعطيت كل بوت صلاحية "Post Messages"

### الملفات
- [ ] استنسخت/رفعت المشروع على GitHub
- [ ] نسخت `config/pages.json.example` إلى `config/pages.json`
- [ ] عدّلت `telegram_channel_id` لكل صفحة
- [ ] حمّلت خط عربي (Cairo Bold) إلى `fonts/arabic.ttf`
- [ ] صممت/تركت 4 قوالب في `templates/`

### GitHub Secrets
- [ ] `GEMINI_API_KEY`
- [ ] `TG_TOKEN_PAGE_1`
- [ ] `TG_TOKEN_PAGE_2`
- [ ] `TG_TOKEN_PAGE_3`
- [ ] `TG_TOKEN_PAGE_4`

### الإعدادات
- [ ] Settings → Actions → Workflow permissions → Read and write
- [ ] جرّبت تشغيل manual عبر Actions tab بـ dry-run
- [ ] جرّبت تشغيل حقيقي (بدون dry-run)
- [ ] شفت منشور فعلي في قناة تيليغرام

🎉 **إذا أكملت كل ما سبق، النظام يشتغل تلقائياً كل ساعة!**

---

## المرحلة 2: إضافة فيسبوك (3 أيام - أسبوعين)

### إعداد Meta
- [ ] حساب Meta for Developers
- [ ] تطبيق Business جديد
- [ ] أضفت "Facebook Login" للتطبيق
- [ ] أضفت "Instagram Graph API" للتطبيق
- [ ] حصلت على App ID و App Secret

### الصفحات
- [ ] 4 صفحات فيسبوك جاهزة (أنت أدمن فيها)
- [ ] 4 حسابات انستغرام (تم تحويلها إلى Business)
- [ ] كل حساب انستغرام مربوط بصفحة فيسبوك
- [ ] حفظت Page IDs الأربعة
- [ ] حفظت Instagram Business IDs الأربعة

### التوكنات
- [ ] حصلت على Short-Lived User Token بالصلاحيات المطلوبة
- [ ] استخدمت `tools/refresh_fb_token.py` للحصول على Long-Lived Page Tokens
- [ ] حفظت توكنات الصفحات الأربعة

### App Review (للصفحات التي لست أدمن فيها فقط)
- [ ] قدمت طلب App Review
- [ ] رفعت فيديو يوضح الاستخدام
- [ ] انتظرت موافقة Meta

### الإعدادات
- [ ] حدّثت `config/pages.json` بـ Page IDs و IG IDs
- [ ] أضفت في GitHub Secrets:
  - [ ] `FB_TOKEN_PAGE_1`
  - [ ] `FB_TOKEN_PAGE_2`
  - [ ] `FB_TOKEN_PAGE_3`
  - [ ] `FB_TOKEN_PAGE_4`
- [ ] جرّبت dry-run وتأكدت من النجاح
- [ ] جرّبت تشغيل حقيقي

---

## المرحلة 3: المراقبة المستمرة

- [ ] أنشأت بوت إشعارات إدارية
- [ ] أضفت `TELEGRAM_ADMIN_BOT_TOKEN` و `TELEGRAM_ADMIN_CHAT_ID` للأسرار
- [ ] جرّبت إرسال إشعار تجريبي
- [ ] أضفت تذكير في تقويمك كل 55 يوم لتجديد توكنات فيسبوك
- [ ] فحصت Actions tab خلال 48 ساعة الأولى للتأكد من الاستقرار

---

## أوامر سريعة للنسخ

```bash
# اختبار محلي
pip install -r requirements.txt
python verify.py

# تشغيل تجريبي
python main.py --dry-run

# تشغيل صفحة واحدة
python main.py --page=page_general

# تجديد توكن فيسبوك (قبل انتهاء صلاحيته)
python tools/refresh_fb_token.py SHORT_LIVED_TOKEN PAGE_ID
```
