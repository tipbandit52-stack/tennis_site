from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api

# --- .env ---
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core ---
SECRET_KEY = os.getenv('SECRET_KEY', 'замени-на-секретный-ключ')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# --- ALLOWED HOSTS ---
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "tennis-site.onrender.com",
    "litetennis.kz",
    "www.litetennis.kz",
]

# --- CSRF / Cookies ---
CSRF_TRUSTED_ORIGINS = [
    "https://tennis-site.onrender.com",
    "https://litetennis.kz",
    "https://www.litetennis.kz",
]
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# --- Apps ---
INSTALLED_APPS = [
    # внешние
    'cloudinary',
    'cloudinary_storage',
    'widget_tweaks',
    'channels',

    # твои
    'api',
    'tournaments',
    'friends',
    'chat',
    'matches',
    'users',
    'players',

    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tennis_site.urls'

# --- Templates ---
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

# --- ASGI / Channels ---
ASGI_APPLICATION = "tennis_site.asgi.application"
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

# --- Database ---
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- I18N ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

# --- Static ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Media ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Cloudinary ---
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")  # формат: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
if CLOUDINARY_URL and CLOUDINARY_URL.startswith("cloudinary://"):
    cloudinary.config(cloudinary_url=CLOUDINARY_URL, secure=True)
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    print("✅ Cloudinary успешно сконфигурирован.")
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    print("⚠️ Cloudinary не настроен, используется локальное хранилище.")

# --- Auth redirects ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'my_profile'
LOGOUT_REDIRECT_URL = 'index'

# --- API Key ---
UNIVERSAL_API_KEY = os.getenv('UNIVERSAL_API_KEY', 'super-secret-key-123')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
