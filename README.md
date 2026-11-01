# سامانه مدیریت کتابخانه

API مدیریت کتاب‌ها با FastAPI و PostgreSQL. داده‌ها در جدول `books` ذخیره می‌شوند و با راه‌اندازی مجدد برنامه باقی می‌مانند. برنامه مستقیماً به سرور PostgreSQL شما وصل می‌شود؛ Docker لازم نیست.

## راه‌اندازی

پیش‌نیازها: Python 3.10+ و یک سرور PostgreSQL روشن و قابل دسترسی. pgAdmin فقط ابزار مدیریت است؛ از اطلاعات اتصال همان سروری که در pgAdmin ثبت کرده‌اید استفاده کنید.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

قبل از اجرای برنامه، مقدار `DATABASE_URL` داخل `.env` را با آدرس PostgreSQL خودتان جایگزین کنید:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

فرمت آدرس `postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE` است. اگر رمز عبور کاراکترهایی مثل `@`, `:`, `/` یا `#` دارد، باید URL-encode شود. برنامه هنگام شروع به دیتابیس وصل شده و جدول `books` را در همان دیتابیس ایجاد می‌کند؛ کاربر دیتابیس باید اجازه ساخت جدول داشته باشد. اگر PostgreSQL روی همین کامپیوتر است معمولاً `HOST` برابر `localhost` است.

## مسیرهای API

| متد | مسیر | کارکرد |
|---|---|---|
| GET | `/books` | فهرست کتاب‌ها |
| POST | `/books` | ایجاد کتاب |
| GET | `/books/{id}` | دریافت کتاب |
| PATCH | `/books/{id}` | ویرایش جزئی |
| DELETE | `/books/{id}` | حذف کتاب |

مستندات تعاملی: `http://127.0.0.1:8000/docs`. درخواست‌ها و پاسخ‌های API مانند قبل هستند؛ شناسه ویرایش یا حذف نمی‌شود و برای کتاب ناموجود پاسخ 404 برمی‌گردد.
