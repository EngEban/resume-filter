<div align="center" dir="rtl">

# 📄 ResumeFilter

**نظام فرز السير الذاتية المدعوم بالذكاء الاصطناعي مع محرك ATS شفاف**

[![Tests](https://github.com/your-username/resume-filter/actions/workflows/test.yml/badge.svg)](https://github.com/your-username/resume-filter/actions/workflows/test.yml)
[![Lint](https://github.com/your-username/resume-filter/actions/workflows/lint.yml/badge.svg)](https://github.com/your-username/resume-filter/actions/workflows/lint.yml)
[![Docker](https://github.com/your-username/resume-filter/actions/workflows/docker.yml/badge.svg)](https://github.com/your-username/resume-filter/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[🇬🇧 English](README.md) · [المعمارية](docs/architecture.md) · [توثيق API](docs/api.md)

</div>

---

<div dir="rtl">

## 🎯 ما هو ResumeFilter؟

منصة متعددة المستأجرين بمستوى إنتاجي، تساعد:
- **المؤسسات** على فرز مئات السير الذاتية في دقائق.
- **الأفراد** على تحسين سيرهم الذاتية لوظيفة محددة.

تجمع بين **محرك ATS شفاف من 6 عوامل** و**طبقة تجريد لمزودي الذكاء الاصطناعي** (أكثر من 100 مزود عبر LiteLLM).

---

## ✨ المميزات

### للمؤسسات (B2B)
- 📦 **معالجة دفعات** — ارفع مئات السير، احصل على تقييم متوازٍ.
- 🏢 **Multi-tenancy** — عزل كامل للبيانات عبر PostgreSQL Row-Level Security.
- 🔑 **BYOK** — اربط OpenAI أو Anthropic أو Gemini أو Groq أو Azure أو Bedrock أو Ollama محلي.
- 📊 **تقارير قائمة قصيرة** — مرشحون مرتّبون مع تفصيل كل عامل.
- 👥 **أدوار** — Owner / Admin / Member / Viewer.
- 🎛️ **Fallback تلقائي** — استخدم المزود المدمج أو مزودك الخاص.

### للأفراد (B2C)
- 🎯 **درجة ATS فورية** مقابل أي وصف وظيفي.
- 🔍 **تحليل فجوات الكلمات المفتاحية** — اعرف ما ينقصك بالضبط.
- 💡 **اقتراحات مرتّبة** — بحسب الأولوية (عالية/متوسطة/منخفضة).
- 📜 **سجل التحليلات** — تتبّع تقدمك.
- 🆓 **خطة مجانية** — 3 تحليلات يومياً.

### نقاط القوة الهندسية
- ⚡ **Async-first** — FastAPI + asyncpg + httpx.
- 🔀 **Celery + Chord** — Fan-out/Fan-in للدفعات.
- 🛡️ **دفاع بعمق** — JWT + Fernet + RLS + BCrypt.
- 📈 **تسجيل منظّم** — JSON logs مع request IDs للتتبع.
- 🐳 **Docker جاهز** — Multi-stage builds بحجم ~200 MB.
- ☸️ **Kubernetes جاهز** — KEDA autoscaling.
- 🧪 **مُختبَر** — Pytest + Ruff + Mypy في CI.

---

## 🏗️ المعمارية
┌─────────────────────────────────────────────────────────────┐
│ واجهة المستخدم NiceGUI (/ui) │
└──────────────────────────┬──────────────────────────────────┘
│
┌──────────────────────────▼──────────────────────────────────┐
│ Backend FastAPI (/api/v1) │
│ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌────────────┐ │
│ │ المصادقة │ │ B2C │ │ B2B │ │ الإعدادات │ │
│ └──────────┘ └──────────┘ └───────────┘ └────────────┘ │
└────┬─────────────┬──────────────┬──────────────┬────────────┘
▼ ▼ ▼ ▼
┌─────────┐ ┌──────────┐ ┌───────────┐ ┌───────────────┐
│Postgres │ │ Redis │ │ MinIO │ │ Celery Worker │
│ + RLS │ │ + Queue │ │ (ملفات) │ │ (متوازي) │
└─────────┘ └──────────┘ └───────────┘ └───────┬───────┘
▼
┌───────────────────┐
│ LiteLLM (100+) │
│ Groq, OpenAI, ... │
└───────────────────┘

text

التفاصيل الكاملة في [docs/architecture.md](docs/architecture.md).

---

## 🚀 التشغيل السريع

### المتطلبات
- Docker Desktop (مع Compose v2)
- Python 3.12+ (للتطوير المحلي)

### 1. نسخ وإعداد

```bash
git clone https://github.com/your-username/resume-filter.git
cd resume-filter
cp .env.example .env
python scripts/generate_master_key.py
انسخ القيم المولّدة إلى .env (SECRET_KEY، MASTER_KEY).

2. احصل على مفتاح Groq مجاني
سجّل في console.groq.com والصق المفتاح:

env
PLATFORM_LLM_API_KEY=gsk_xxxxxxxxxxxx
3. شغّل كل شيء
bash
docker-compose -f docker/docker-compose.yml up -d --build
4. افتح المتصفح
الخدمة	الرابط
واجهة المستخدم	http://localhost:8000/ui
توثيق API	http://localhost:8000/docs
Celery Flower	http://localhost:5555
MinIO Console	http://localhost:9001
بيانات MinIO الافتراضية: minioadmin / minioadmin.

📁 هيكل المشروع
text
resume-filter/
├── app/                    # Backend FastAPI
│   ├── api/v1/             # نقاط REST
│   ├── core/               # إعدادات + أمان + logging
│   ├── db/                 # نماذج SQLAlchemy + RLS
│   ├── providers/          # تجريد مزودي LLM
│   ├── services/           # منطق العمل
│   ├── workers/            # مهام Celery
│   └── schemas/            # نماذج Pydantic
├── ui/                     # واجهة NiceGUI
├── docker/                 # Dockerfiles + Compose
├── k8s/                    # ملفات Kubernetes
├── alembic/                # ترحيلات قاعدة البيانات
├── tests/                  # اختبارات Pytest
├── scripts/                # سكريبتات
└── docs/                   # التوثيق
🧪 الاختبارات
bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app
ruff check app ui tests
mypy app ui
🛠️ التقنيات
الطبقة	التقنية
Backend	FastAPI 0.115, Python 3.12
قاعدة البيانات	PostgreSQL 16 (مع RLS)
ORM	SQLAlchemy 2.0 (async) + Alembic
قائمة المهام	Celery 5.4 + Redis 7
التخزين	MinIO (متوافق S3)
LLM	LiteLLM (100+ مزود)
المصادقة	JWT + BCrypt
التشفير	Fernet
الواجهة	NiceGUI 2.9 (Python فقط)
Logging	structlog
الاختبار	pytest + coverage
Linting	Ruff + Mypy
CI/CD	GitHub Actions
الحاويات	Docker + Compose
التنسيق	Kubernetes + KEDA
🔒 الأمان
عزل متعدد المستأجرين — RLS + سياق لكل طلب.

مفاتيح مشفّرة — Fernet قبل التخزين.

كلمات مرور مُجزّأة — BCrypt.

JWT — توكنات قصيرة العمر.

حماية من Prompt Injection — System prompts صارمة.

سياسات RLS — حزامان (ORM + DB).

للإبلاغ عن ثغرة أمنية، راجع SECURITY.md.

📖 التوثيق
المعمارية

مرجع API

دليل المساهمة

📄 الترخيص
MIT — راجع LICENSE.

<div align="center">
بُني بـ ❤️ باستخدام Python و FastAPI و NiceGUI.

</div> ```