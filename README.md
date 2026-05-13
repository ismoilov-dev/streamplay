# StreamPlay API 🎬

**Video on Demand (VOD) platformasi** uchun Django REST API. Netflix/Kinopoisk uslubidagi video striming xizmat backendi.

## 🚀 Xususiyatlari

- ✅ **JWT Autentifikatsiya** (djangorestframework-simplejwt)
- ✅ **Swagger/OpenAPI hujjat** (drf-spectacular) — `/api/docs/`
- ✅ **Filmlar, seriallar, fasllar, epizodlar** — to'liq CRUD
- ✅ **Video fayllar** — turli sifat variantlari (480p, 720p, 1080p, 4K), HLS/DASH
- ✅ **Subtitrlar va Audio treklar** — ko'p tilli qo'llab-quvvatlash
- ✅ **Obuna tizimi (SVOD)** — Basic/Standard/Premium rejalar
- ✅ **Ko'rish progressi** — "Qayerda to'xtagan edim?" funksiyasi
- ✅ **Ko'rish tarixi** va **Sevimlilar**
- ✅ **Tavsiyalar tizimi** — content-based + o'xshash filmlar
- ✅ **Qidiruv** — filmlar, seriallar, aktyorlar, janrlar bo'yicha
- ✅ **Analytics** — buffering eventlari (QoE monitoring)
- ✅ **Chunked Upload** — katta video fayllarni bo'laklab yuklash (Tus-like)
- ✅ **CORS** — frontenddan so'rovlar uchun
- ✅ **Filtering, Ordering, Pagination** — barcha ro'yxatlar uchun

## 📦 Texnologiyalar

- Python 3.10+
- Django 5.0
- Django REST Framework 3.15
- SQLite (tez ishga tushirish uchun; PostgreSQL-ga oson almashtiriladi)
- drf-spectacular (Swagger/OpenAPI 3)
- Simple JWT
- django-filter, django-cors-headers

## ⚡ Tez ishga tushirish

### 1. Paketlarni o'rnatish

```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Bazani tayyorlash

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Demo ma'lumotlarni yaratish (ixtiyoriy, lekin tavsiya qilinadi)

```bash
python manage.py seed_data
```

Bu quyidagilarni yaratadi:
- **Admin**: `admin` / `admin123`
- **Foydalanuvchi**: `user1` / `user12345`
- 10 ta film, 4 ta serial (fasllar + epizodlar bilan)
- 10 ta janr, 12 ta aktyor
- 3 ta obuna rejasi

### 4. Serverni ishga tushirish

```bash
python manage.py runserver
```

## 📚 URL-lar

| Manzil | Tavsif |
|---|---|
| `http://127.0.0.1:8000/` | Root — API haqida ma'lumot |
| `http://127.0.0.1:8000/api/docs/` | **Swagger UI** |
| `http://127.0.0.1:8000/api/redoc/` | ReDoc |
| `http://127.0.0.1:8000/api/schema/` | OpenAPI JSON |
| `http://127.0.0.1:8000/admin/` | Django Admin |

## 🔑 Autentifikatsiya

### Ro'yxatdan o'tish

```bash
POST /api/auth/register/
{
  "username": "newuser",
  "email": "new@example.com",
  "password": "StrongPass123",
  "password2": "StrongPass123"
}
```

### Kirish (login) — JWT token olish

```bash
POST /api/auth/login/
{
  "username": "admin",
  "password": "admin123"
}
```

Javob:
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": { "id": 1, "username": "admin", ... }
}
```

### Token orqali so'rov yuborish

```bash
GET /api/users/me/
Authorization: Bearer <access_token>
```

Swagger UI da yuqoridagi **"Authorize"** tugmasini bosib, `Bearer eyJ...` ko'rinishida kiriting.

## 📁 Asosiy endpointlar

### Kontent
- `GET    /api/movies/` — filmlar ro'yxati (filtering, search, ordering)
- `GET    /api/movies/trending/` — trend filmlar
- `GET    /api/movies/new-releases/` — yangi chiqqanlar
- `GET    /api/movies/{slug}/` — bitta film tafsilotlari
- `POST   /api/movies/{slug}/increment-views/` — ko'rishlar +1
- `GET    /api/series/` — seriallar
- `GET    /api/series/{slug}/` — serial + fasllar + epizodlar
- `GET    /api/search/?q=batman` — umumiy qidiruv

### Obunalar
- `GET  /api/subscriptions/plans/` — mavjud rejalar
- `POST /api/subscriptions/subscribe/` — rejaga obuna bo'lish
- `GET  /api/subscriptions/my-subscription/` — hozirgi obuna

### Ko'rish
- `POST /api/analytics/progress/update/` — progressni saqlash (har 10s)
- `GET  /api/analytics/progress/continue-watching/` — davom ettirish ro'yxati
- `GET  /api/analytics/history/` — ko'rish tarixi
- `POST /api/analytics/favorites/` — sevimlilarga qo'shish

### Tavsiyalar
- `GET /api/recommendations/movies/for-me/` — sizga mos filmlar
- `GET /api/recommendations/movies/similar/{slug}/` — o'xshash filmlar
- `GET /api/recommendations/series/for-me/`

### Chunked Upload
```
1. POST /api/uploads/initiate/              — sessiya ochish
2. POST /api/uploads/{upload_id}/chunk/     — har bir bo'lakni yuborish
3. POST /api/uploads/{upload_id}/complete/  — birlashtirish
   GET  /api/uploads/{upload_id}/status/    — holatni tekshirish
```

## 🗂 Loyiha strukturasi

```
streamplay/
├── config/              # Asosiy Django sozlamalari (settings, urls, wsgi)
├── accounts/            # Foydalanuvchi modeli, JWT, auth
├── content/             # Movie, Series, Season, Episode, VideoFile, Genre, Actor, Subtitle
├── subscriptions/       # SubscriptionPlan, Subscription, Payment
├── analytics/           # WatchProgress, WatchHistory, BufferingEvent, Favorite
├── recommendations/     # Tavsiyalar algoritmi
├── uploads/             # Chunked fayl yuklash
├── media/               # Yuklangan fayllar
├── manage.py
└── requirements.txt
```

## 🏗 Arxitektura haqida

TZ'ga muvofiq loyiha monolit tarzda qurilgan, ammo ilovalar **alohida servislarga ajratilishga tayyor**:
- `content` + `uploads` → Content service
- `transcoder` (kelajakda, Celery + FFmpeg bilan) → Video Processing service
- `subscriptions` → Billing service
- `analytics` → Analytics service

### Keyingi bosqichda qo'shish mumkin (TZ bo'yicha)

Bu loyiha **to'liq ishlaydigan MVP**. Production uchun quyidagilarni qo'shish tavsiya etiladi:

| Xususiyat | Qanday qo'shiladi |
|---|---|
| **Haqiqiy transkodlash** | `ffmpeg-python` + Celery worker. `content/tasks.py` yozish |
| **S3 / MinIO storage** | `django-storages[boto3]` + settings'ga `DEFAULT_FILE_STORAGE` |
| **CloudFront Signed URLs** | `boto3` bilan CloudFront signer |
| **DRM (AES-128)** | FFmpeg `-hls_key_info_file` opsiyasi |
| **Elasticsearch qidiruv** | `django-elasticsearch-dsl` — `content/documents.py` yozish |
| **Redis keshlash** | `django-redis` + `CACHES['default']['BACKEND']` |
| **PostgreSQL** | `DATABASES` ni o'zgartirish |
| **Celery + Redis** | Transkodlash, analytics async tasklar uchun |
| **Docker + Kubernetes** | API va Worker pod'larini alohida auto-scaling qilish |

## 🧪 Test qilish

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. Filmlar ro'yxati
curl http://127.0.0.1:8000/api/movies/

# 3. Qidiruv
curl "http://127.0.0.1:8000/api/search/?q=inception"
```

## 📄 Litsenziya

Bu o'quv loyihasi — istalgancha foydalanishingiz mumkin.

---

**Swagger UI-ni ishga tushiring:** `http://127.0.0.1:8000/api/docs/` 🚀
