import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(ROOT_DIR / '.env', override=False)
PACKETA_API_KEY = os.getenv("PACKETA_API_KEY", "")


SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
DEBUG = os.getenv('DEBUG', '1') == '1'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # project apps
    'apps.core',
    'apps.pages',
    'apps.catalog',     # ← TOTO JE DŮLEŽITÉ
    'apps.cart',
    'apps.checkout',
    'apps.orders',
    'apps.payments',
    'apps.accounts',
    'apps.shipping',
    'apps.inventory',
    "widget_tweaks",

]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ROOT_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.cart.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Dev: SQLite; Prod: DATABASE_URL (Postgres)
default_db = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ROOT_DIR / "db.sqlite3",
}

db_url = os.getenv("DATABASE_URL", "").strip()
if db_url:
    DATABASES = {"default": dj_database_url.parse(db_url)}
else:
    DATABASES = {"default": default_db}

# Internationalization
LANGUAGE_CODE = 'cs'
TIME_ZONE = 'Europe/Prague'
USE_I18N = True
USE_TZ = True

# Static & media
STATIC_URL = '/static/'
STATIC_ROOT = ROOT_DIR / 'staticfiles'
STATICFILES_DIRS = [ROOT_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = ROOT_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Emails
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', '0') == '1'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', '0') == '1'

# Payments (placeholders)
GOPAY_GOID = os.getenv('GOPAY_GOID', '')
GOPAY_CLIENT_ID = os.getenv('GOPAY_CLIENT_ID', '')
GOPAY_CLIENT_SECRET = os.getenv('GOPAY_CLIENT_SECRET', '')

# Shipping
COD_FEE = os.getenv('COD_FEE', '0')
ENABLE_APPLE_PAY = os.getenv('ENABLE_APPLE_PAY', '0') == '1'
ENABLE_GOOGLE_PAY = os.getenv('ENABLE_GOOGLE_PAY', '0') == '1'
