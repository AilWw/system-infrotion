# Abu Suhail E-Commerce System - Django Version

نظام متكامل للتجارة الإلكترونية مبني بـ Django مع دعم كامل للعربية والإنجليزية.

## المميزات الرئيسية

- ✅ دعم كامل للعربية (RTL) والإنجليزية (LTR)
- ✅ كتالوج منتجات مع فئات وتصفية
- ✅ سلة التسوق والدفع الآمن
- ✅ نظام التقييمات والتعليقات
- ✅ لوحة تحكم إدارية متقدمة
- ✅ تخصيص الموقع (الألوان، الشعار، معلومات التواصل)
- ✅ إدارة الطلبات والعملاء
- ✅ تكامل Stripe للدفع

## المتطلبات

- Python 3.8+
- pip أو pip3
- Virtual Environment

## التثبيت

### 1. فك ضغط الملف

```bash
tar -xzf abu_suhail_django.tar.gz
cd abu_suhail_django
```

### 2. إنشاء بيئة افتراضية

```bash
python3 -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate  # على Windows
```

### 3. تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### 4. إعداد متغيرات البيئة

```bash
cp .env.example .env
# ثم عدّل ملف .env بمفاتيح Stripe والإعدادات الأخرى
```

### 5. تشغيل الترحيلات

```bash
python manage.py migrate
```

### 6. إنشاء حساب مسؤول

```bash
python manage.py createsuperuser
```

### 7. تشغيل خادم التطوير

```bash
python manage.py runserver
```

الآن يمكنك الوصول إلى الموقع على: `http://localhost:8000`

## الوصول إلى لوحة التحكم

- رابط لوحة التحكم: `http://localhost:8000/admin/`
- استخدم بيانات المسؤول التي أنشأتها

## الهيكل

```
abu_suhail_django/
├── ecommerce/           # إعدادات المشروع الرئيسية
│   ├── settings.py      # الإعدادات
│   ├── urls.py          # المسارات الرئيسية
│   └── wsgi.py          # WSGI
├── store/               # تطبيق المتجر
│   ├── models.py        # نماذج قاعدة البيانات
│   ├── views.py         # العروض
│   ├── urls.py          # مسارات المتجر
│   └── admin.py         # إدارة لوحة التحكم
├── templates/           # قوالب HTML
│   ├── base.html        # القالب الأساسي
│   ├── store/           # قوالب المتجر
│   └── admin/           # قوالب الإدارة
├── static/              # ملفات ثابتة (CSS, JS, صور)
├── media/               # ملفات تحميل المستخدمين
├── manage.py            # سكريبت إدارة Django
└── requirements.txt     # المكتبات المطلوبة
```

## الميزات الرئيسية

### 1. كتالوج المنتجات
- عرض المنتجات بشكل شبكي
- تصفية حسب الفئات
- البحث عن المنتجات
- عرض التفاصيل والصور

### 2. السلة والدفع
- إضافة/حذف المنتجات من السلة
- حساب الضرائب والشحن تلقائياً
- دفع آمن عبر Stripe
- تتبع الطلبات

### 3. النظام الإداري
- إدارة المنتجات والفئات
- إدارة الطلبات والعملاء
- تخصيص الموقع (الألوان، الشعار، معلومات التواصل)
- إدارة الخصومات والعروض

### 4. التقييمات والتعليقات
- إضافة تقييمات للمنتجات
- عرض متوسط التقييمات
- إدارة التعليقات

## الأوامر المهمة

```bash
# تشغيل خادم التطوير
python manage.py runserver

# إنشاء ترحيلات جديدة
python manage.py makemigrations

# تطبيق الترحيلات
python manage.py migrate

# إنشاء مسؤول جديد
python manage.py createsuperuser

# جمع الملفات الثابتة
python manage.py collectstatic

# تشغيل الاختبارات
python manage.py test
```

## الدعم والمساعدة

إذا واجهت أي مشاكل:

1. تأكد من تثبيت جميع المكتبات: `pip install -r requirements.txt`
2. تأكد من إنشاء قاعدة البيانات: `python manage.py migrate`
3. تأكد من إعدادات Stripe في ملف `.env`
4. جرب حذف ملف `db.sqlite3` وإعادة الترحيلات

## الترخيص

هذا المشروع مرخص تحت MIT License

---

**تم بناء هذا المشروع بـ Django 5.2.10**
