# 🚀 Kaaro

An On-Demand Service Marketplace built with Django REST Framework.

Kaaro is a backend-focused project where users can request home services (cleaning, repairs, moving, etc.) and specialists can accept and complete jobs.  
The system uses Redis for OTP caching and Celery for background tasks like sending SMS notifications.

---

## ✨ Key Features

✅ OTP-based authentication (request OTP & login)  
✅ JWT authentication stored securely in **HTTP-only cookies** (`accessToken`, `refreshToken`)  
✅ Role-based system: **Customer / Specialist**  
✅ Specialist onboarding workflow (users request, admin approves via admin panel)  
✅ Task-based service marketplace (customers create service requests)  
✅ Approved specialists can view available tasks, accept them, and manage job lifecycle  
✅ Concurrency-safe task assignment (tasks are locked after acceptance)  
✅ Task lifecycle management: Pending → Accepted → In Progress → Done / Canceled  
✅ Redis caching for OTP codes with automatic expiration  
✅ Celery background workers for asynchronous OTP SMS delivery  
✅ Fully tested APIs using **Pytest**  
✅ API documentation generated with **Swagger (drf-spectacular)**


## 🛠️ Tech Stack

- **Python 3.11+**
- **Django REST Framework (DRF)**
- **PostgreSQL**
- **Redis**
- **Celery**

---

## 🚀 How to run the project

### ⚙️ Create a `.env` file
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost

REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

FARAZ_SMS_API_KEY=key
FARAZ_SMS_LOGIN_OTP_PATTERN_CODE=code
FARAZ_SMS_SENDER_NUMBER=123
FARAZ_SMS_PHONE_BOOK_ID=123
```

📦 Install requirements
```bash
# Create virtual environment
python -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

```
🔥 Run the project
```bash
# Run migrations
python manage.py migrate

# Start server
python manage.py runserver

# Start celery worker
celery -A kaaro worker --loglevel=INFO --pool=solo
```

## 🧪 API Documentation

* Swagger: `http://localhost:8000/swagger/`

Developed with ❤️ by **Ramin👑**
