# 🚗 AutoCare

A Car Service Booking & Management System built with Django REST Framework.

AutoCare is a backend-focused project where users can register their cars, request service appointments, and authenticate via OTP.  
The system uses Redis for OTP caching and Celery for background tasks like sending SMS notifications.

---

## ✨ Key Features

✅ OTP Authentication (request OTP + login)  
✅ JWT authentication stored in **cookies** (`accessToken`, `refreshToken`)  
✅ Car management (users can register and manage cars)  
✅ Booking appointments for service centers  
✅ Redis caching for OTP codes (expires automatically)  
✅ Celery background tasks (send OTP SMS asynchronously)  
✅ API Documentation using Swagger

## 🛠️ Tech Stack

* **Python 3.11+**
* **Django REST Framework (DRF)**
* **PostgreSQL**


## 🚀 How to run the project

⚙️ Create a `.env` file:
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
celery -A carservices worker --loglevel=INFO --pool=solo
```

## 🧪 API Documentation

* Swagger: `http://localhost:8000/swagger/`

Developed with ❤️ by **Ramin👑**
