from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# =======================
# .env
# =======================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =======================
# Основные настройки
# =======================
SECRET_KEY = os.getenv('SECRET_KEY', 'замени-на-секретный-ключ')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# =======================
# CSRF / Cookies
# =======================
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://tennis-site.onrender.com",  # адрес твоего хостинга Render
]

SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# =======================
# Приложения
# =======================
INSTALLED_APPS = [
    # Внешние пакеты
    'cloudinary',
    'cloudinary_storage',
    'widget_tweaks',
    'channels',

    # Твои приложения
    'api',
    'tournaments',
    'friends',
    'chat',
    'matches',
    'users',
    'players',

    # Django системные
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# =======================
# Middleware
# =======================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ⚡ для статики на Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tennis_site.urls'

# =======================
# Templates
# =======================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# =======================
# ASGI / Channels
# =======================
ASGI_APPLICATION = "tennis_site.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# =======================
# База данных
# =======================
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# =======================
# Проверка паролей
# =======================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =======================
# Локализация
# =======================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

# =======================
# Статика и медиа
# =======================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Локальные медиа (используются только при DEBUG=True)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =======================
# Cloudinary (для Render)
# =======================
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')

# =======================
# Авторизация
# =======================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'my_profile'
LOGOUT_REDIRECT_URL = 'index'

# =======================
# Универсальный API ключ
# =======================
UNIVERSAL_API_KEY = os.getenv('UNIVERSAL_API_KEY', 'super-secret-key-123')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =======================
# Cloudinary конфигурация (фиксация ошибки "Invalid CLOUDINARY_URL")
# =======================
# =======================
# Cloudinary (хранение фото)
# =======================
import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if CLOUDINARY_URL and CLOUDINARY_URL.startswith("cloudinary://"):
    cloudinary.config(cloudinary_url=CLOUDINARY_URL)
else:
    print("⚠️ Внимание: CLOUDINARY_URL не найден или имеет неверный формат!")

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
