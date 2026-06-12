# 🤖 وكيل الأخبار العراقية - النسخة الإنتاجية

نظام آلي متكامل لجمع الأخبار العراقية ونشرها تلقائياً على:
- 📱 **تيليغرام** (الأسهل - يشتغل في 30 دقيقة)
- 📘 **فيسبوك** (يحتاج موافقة Meta - 3 أيام لأسبوعين)
- 📷 **انستغرام** (نفس متطلبات فيسبوك)

كل شي مجاني 100% عبر GitHub Actions و Google Gemini و RSS مجاني.

---

## 🚀 طريقة "الإقلاع السريع" (30 دقيقة - تيليغرام فقط)

لو تريد تشغّل النظام **اليوم**، ابدأ بتيليغرام واترك فيسبوك للاحقاً:

### الخطوة 1: GitHub (5 دقائق)
1. أنشئ حساب GitHub لو ما عندك
2. أنشئ repo جديد فاضي اسمه `news-agent` (خاص أو عام - عام يعطيك تشغيل مجاني غير محدود)
3. ارفع ملفات هذا المشروع للريبو

### الخطوة 2: Google Gemini (3 دقائق)
1. ادخل [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. سجّل دخول بحساب جوجل
3. اضغط **Create API Key** → انسخ المفتاح

### الخطوة 3: بوتات تيليغرام (10 دقائق - 4 بوتات)
1. افتح تيليغرام وكلّم [@BotFather](https://t.me/BotFather)
2. أرسل `/newbot` واتبع التعليمات (4 مرات - بوت لكل صفحة)
3. احفظ التوكن الذي يعطيك إياه لكل بوت

### الخطوة 4: قنوات تيليغرام (5 دقائق - 4 قنوات)
1. أنشئ 4 قنوات (للأخبار العامة، السياسة، الرياضة، الاقتصاد)
2. في كل قناة: Settings → Administrators → أضف البوت الخاص بها
3. أعطه صلاحية **Post Messages**
4. احفظ معرف القناة: مثلاً `@iraq_news_general`

### الخطوة 5: قوالب التصميم (10 دقائق)
- **الخيار السريع:** استخدم القوالب الأولية في `templates/` (تعمل فوراً)
- **الخيار الأفضل:** صمم 4 قوالب احترافية على [Canva](https://canva.com) بمقاس 1080×1080 وضعها في `templates/`

### الخطوة 6: الخط العربي (دقيقتين)
1. حمّل [Cairo Bold من Google Fonts](https://fonts.google.com/specimen/Cairo)
2. أعد تسميته إلى `arabic.ttf`
3. ضعه في `fonts/arabic.ttf`

### الخطوة 7: الإعدادات
1. انسخ `config/pages.json.example` إلى `config/pages.json`
2. عدّل `telegram_channel_id` لكل صفحة (مثلاً `@iraq_news_general`)
3. ادفع للريبو: `git add . && git commit -m "إعداد" && git push`

### الخطوة 8: أسرار GitHub
في GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

أضف:
| اسم السر | القيمة |
|---|---|
| `GEMINI_API_KEY` | مفتاح Gemini |
| `TG_TOKEN_PAGE_1` | توكن البوت الأول |
| `TG_TOKEN_PAGE_2` | توكن البوت الثاني |
| `TG_TOKEN_PAGE_3` | توكن البوت الثالث |
| `TG_TOKEN_PAGE_4` | توكن البوت الرابع |

### الخطوة 9: تشغيل!
1. ادخل **Actions** في الريبو
2. اختر **"تشغيل وكيل الأخبار العراقية"**
3. اضغط **Run workflow**
4. شاهد السحر يحدث ✨

من الآن، سيشتغل كل ساعة تلقائياً.

---

## 📘 إضافة فيسبوك وانستغرام (المرحلة الثانية)

بعد أن يشتغل تيليغرام بنجاح، يمكنك إضافة فيسبوك وانستغرام:

### الخطوة 1: حساب Meta Developer
1. ادخل [developers.facebook.com](https://developers.facebook.com)
2. أنشئ تطبيقاً نوع **Business**
3. أضف المنتجات: **Facebook Login** و **Instagram Graph API**

### الخطوة 2: ربط انستغرام Business
كل صفحة من صفحاتك الأربع تحتاج:
- حساب انستغرام تم تحويله إلى Business أو Creator
- ربط الحساب بصفحة فيسبوك (من إعدادات الانستغرام)

### الخطوة 3: الحصول على Page Access Tokens
1. ادخل [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. اطلب الصلاحيات:
   - `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`
   - `instagram_basic`, `instagram_content_publish`
   - `business_management`
3. اختر صفحتك → انسخ التوكن
4. **حوّله إلى Long-Lived (60 يوم)** باستخدام:
   ```bash
   python tools/refresh_fb_token.py <SHORT_LIVED_TOKEN> <PAGE_ID>
   ```

### الخطوة 4: App Review (الجزء الذي يأخذ وقت)
لتنشر على صفحات لست أدمن فيها، يجب أن:
1. تقدم طلب App Review في تطبيقك
2. تشرح كيف ستستخدم كل صلاحية
3. ترفع فيديو يوضح الاستخدام
4. تنتظر 3 أيام - أسبوعين

⚠️ **خبر سار:** للصفحات التي أنت أدمن فيها، التطبيق في وضع التطوير (Dev Mode) يشتغل **فوراً** بدون App Review. يعني تقدر تنشر على صفحاتك الأربع مباشرة!

### الخطوة 5: تحديث الإعدادات
أضف القيم في `config/pages.json`:
```json
"facebook_page_id": "123456789",
"instagram_account_id": "17841400000000",
"facebook_token_env": "FB_TOKEN_PAGE_1"
```

وفي GitHub Secrets:
- `FB_TOKEN_PAGE_1`, `FB_TOKEN_PAGE_2`, إلخ

---

## 🔍 التحقق من السلامة قبل الإطلاق

شغّل سكربت التحقق - يفحص كل شيء:

```bash
python verify.py              # فحص كامل
python verify.py --rss        # مصادر RSS فقط
python verify.py --gemini     # Gemini فقط
python verify.py --pages      # توكنات فيسبوك/انستغرام
python verify.py --telegram   # توكنات تيليغرام
```

---

## 🧪 الاختبار قبل النشر الفعلي

```bash
# تشغيل تجريبي - يولّد الصور ويعرض ما سيُنشر بدون نشر فعلي
python main.py --dry-run

# تشغيل صفحة واحدة فقط (للاختبار)
python main.py --page=page_sports

# دمج الخيارين
python main.py --dry-run --page=page_general
```

---

## ⚠️ ملاحظات مهمة عن "العمل المستمر"

### GitHub Actions cron ليس دقيقاً
- المجدول مكتوب: كل ساعة (`0 * * * *`)
- الواقع: قد يتأخر 15-60 دقيقة في أوقات الذروة
- ⚠️ هذا قيد من GitHub نفسها - لا يوجد حل مع الطبقة المجانية
- ✅ كافٍ تماماً لأخبار - لا أحد يحتاج الدقة لثانية

### حدود الطبقة المجانية
- **GitHub Actions**: 2,000 دقيقة/شهر للريبو الخاص، **غير محدود للريبو العام**
- **Gemini Free**: 1,500 طلب/يوم → كافٍ لـ 4 صفحات كل ساعة (96 طلب فقط)
- **Telegram Bot API**: غير محدود
- **Meta Graph API**: حدود معقولة - لن تصل لها

✨ **التوصية:** استخدم ريبو **عام** (Public) لتشغيل غير محدود. الكود ما فيه أسرار (التوكنات في Secrets منفصلة).

### توكنات فيسبوك تنتهي كل 60 يوم
- ضع تذكير في تقويمك كل 55 يوم
- استخدم `python tools/refresh_fb_token.py` لتجديدها
- اشترك في إشعارات تيليغرام الإدارية لتعرف لما يتعطل النشر

---

## 📊 المراقبة والتحديث

### مراقبة فورية عبر تيليغرام
1. أنشئ بوت إضافي للإشعارات (`@BotFather`)
2. أرسل `/start` للبوت لتفعيله
3. احصل على chat_id من [@userinfobot](https://t.me/userinfobot)
4. أضف في GitHub Secrets:
   - `TELEGRAM_ADMIN_BOT_TOKEN`
   - `TELEGRAM_ADMIN_CHAT_ID`

سيرسل لك إشعار لما:
- ❌ تفشل كل الصفحات في النشر
- ⚠️ تنتهي صلاحية توكن
- 🚨 يحدث خطأ غير متوقع

### مشاهدة Logs
- في GitHub: **Actions → آخر تشغيل → "تشغيل الوكيل"**
- محلياً: `data/logs/agent_YYYYMMDD.log`

### تحديث الكود
```bash
# سحب آخر التحديثات
git pull origin main

# بعد أي تعديل
git add .
git commit -m "تحديث X"
git push
# سيشتغل النظام بالكود الجديد في الجولة التالية
```

---

## 📂 هيكل المشروع المحدث

```
news_agent/
├── main.py                    # نقطة الدخول الإنتاجية
├── verify.py                  # سكربت التحقق من السلامة 🆕
├── requirements.txt
├── .env.example
├── .github/workflows/
│   └── run_agent.yml          # جدولة GitHub Actions (محدّث)
├── config/
│   ├── pages.json.example     # نموذج الإعدادات (مع Telegram 🆕)
│   └── sources.json           # مصادر RSS العراقية
├── src/
│   ├── fetcher.py             # جلب RSS
│   ├── processor.py           # Gemini AI
│   ├── designer.py            # تصميم الصور
│   ├── publisher.py           # فيسبوك + انستغرام
│   ├── telegram_publisher.py  # تيليغرام 🆕
│   ├── storage.py             # سجل المنشورات
│   └── logger.py              # نظام تسجيل منظم 🆕
├── tools/
│   └── refresh_fb_token.py    # تجديد توكنات فيسبوك 🆕
├── templates/                 # 4 قوالب تصميم (أولية)
├── fonts/arabic.ttf           # خط عربي
└── data/                      # سجل المنشورات والـ logs
```

---

## 🆘 حل المشكلات

### المشكلة: `python verify.py --rss` يرجّع أن المصادر لا تعمل
**الحل**: مواقع الأخبار تغيّر روابط RSS بين الحين والآخر. حدّث `config/sources.json` بالروابط الصحيحة:
1. ادخل موقع المصدر مباشرة
2. ابحث في الـ Footer عن أيقونة RSS أو كلمة "RSS"
3. اضغط بزر الفأرة الأيمن → نسخ الرابط

### المشكلة: انستغرام لا ينشر
**الأسباب الشائعة:**
- الحساب ليس Business/Creator → غيّره من إعدادات انستغرام
- غير مرتبط بصفحة فيسبوك → اربطه من الإعدادات
- التوكن لا يحوي صلاحية `instagram_content_publish` → اطلبها

### المشكلة: تيليغرام يرجّع `Bad Request: chat not found`
**الحل:**
- تأكد أن `telegram_channel_id` صحيح (مثلاً `@channelname` بـ `@`)
- البوت ليس أدمن في القناة → اجعله أدمن
- القناة خاصة → استخدم `-100xxxxx` بدلاً من `@name`

### المشكلة: الخط لا يظهر بشكل صحيح
- اسم الملف **بالضبط**: `fonts/arabic.ttf`
- جرّب خطاً مختلفاً (Tajawal بدلاً من Cairo)

### المشكلة: GitHub Actions يفشل بـ "permission denied"
**الحل:** في الريبو → Settings → Actions → General → Workflow permissions → اختر **"Read and write permissions"**

---

## 🔐 الأمان

- ✅ التوكنات في GitHub Secrets (مشفّرة - حتى أنت ما تقدر تراها بعد إدخالها)
- ✅ ملف `.env` في `.gitignore` - لن يُرفع للريبو
- ✅ سجلات الـ logs ما تحوي توكنات
- ⚠️ لا تضع توكنات في الكود مباشرة أبداً
- ⚠️ لو سرقت ريبو خاص، التوكنات محمية في Secrets

---

## ⚖️ الأخلاقيات والقانون

- **ذكر المصدر**: مفعّل بـ `append_source: true` في الإعدادات
- **الصياغة**: الذكاء الاصطناعي يعيد الصياغة، فلا تكرار حرفي
- **المحتوى الحساس**: راجع يدوياً قبل النشر التلقائي (خاصة الأخبار السياسية)
- **سياسة Meta**: التزم بمعدلات النشر المعقولة (كل ساعة آمن جداً)

---

## 🎯 خارطة الطريق (تطويرات مقترحة)

- [ ] **دعم تويتر/X** (يحتاج Twitter Developer Account)
- [ ] **توليد صور AI خاصة بكل خبر** (Stable Diffusion API)
- [ ] **فلاتر ذكية** (كلمات مفتاحية، تجاهل المصادر السلبية)
- [ ] **لوحة تحكم ويب** لمراقبة الأداء
- [ ] **تحليلات** كم منشور حقق تفاعلاً أعلى
- [ ] **دعم الـ Reels** و **Stories**

---

صُمم بـ ❤️ للإعلام العراقي

📧 لأي استفسار، افتح Issue في GitHub
