from __future__ import unicode_literals
import environ
import os
import platform

from dotenv import load_dotenv
from logging.handlers import SysLogHandler

# Populate os.environ with variables from .env (if it exists)
load_dotenv(verbose=True)

# Now parse the pre-populated environment into django-environ
env = environ.Env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'webhook_receiver',
    'webhook_receiver_shopify',
    'webhook_receiver_woocommerce',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    },
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

ROOT_URLCONF = 'webhook_receiver.urls'

# SECURITY WARNING: keep the secret key used in production secret!
# We're setting a default of None here as that will cause Django to
# refuse to start the key isn't set in the environment or in a config
# file.
SECRET_KEY = env.str('DJANGO_SECRET_KEY', default=None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=False)

hostname = platform.node().split(".")[0]
syslog_address = '/var/run/syslog' if platform.system().lower() == 'darwin' else '/dev/log'  # noqa: E501
syslog_format = '[service_variant=webhook_receiver]' \
                '[%(name)s] %(levelname)s [{hostname}  %(process)d] ' \
                '[%(filename)s:%(lineno)d] ' \
                '- %(message)s'.format(hostname=hostname)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(process)d '
                      '[%(name)s] %(filename)s:%(lineno)d - %(message)s',
        },
        'syslog_format': {'format': syslog_format},
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'local': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'address': syslog_address,
            'formatter': 'syslog_format',
            'facility': SysLogHandler.LOG_LOCAL0,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'local'],
            'propagate': False,
            'level': 'INFO'
        },
        'requests': {
            'handlers': ['console', 'local'],
            'propagate': True,
            'level': 'WARNING'
        },
        'factory': {
            'handlers': ['console', 'local'],
            'propagate': True,
            'level': 'WARNING'
        },
        'django.request': {
            'handlers': ['console', 'local'],
            'propagate': True,
            'level': 'WARNING'
        },
        '': {
            'handlers': ['console', 'local'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

# We populate ALLOWED_HOSTS from a comma-separated list. Running with
# DEBUG = True overrides this, and is equivalent to setting the
# DJANGO_ALLOWED_HOSTS envar to "localhost,127.0.0.1,[::1]".
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default="")

# Async task processing via Celery
CELERY_BROKER_URL = env.str('DJANGO_CELERY_BROKER_URL', default="")

# If the broker URL is empty, run Celery in always-eager mode. Define
# both ALWAYS_EAGER (Celery <4) and TASK_ALWAYS_EAGER (Celery >= 4).
CELERY_ALWAYS_EAGER = not bool(CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = not bool(CELERY_BROKER_URL)

DATABASES = {
    'default': env.db('DJANGO_DATABASE_URL',
                      default="sqlite://:memory:"),
}

CACHES = {
    'default': env.cache('DJANGO_CACHE_URL',
                         default="dummycache://"),
}

WEBHOOK_RECEIVER_EDX_OAUTH2_URL_ROOT = env.str(
    'DJANGO_WEBHOOK_RECEIVER_EDX_OAUTH2_URL_ROOT',
    default='http://localhost:18000')
WEBHOOK_RECEIVER_EDX_OAUTH2_KEY = env.str(
    'DJANGO_WEBHOOK_RECEIVER_EDX_OAUTH2_KEY',
    default='')
WEBHOOK_RECEIVER_EDX_OAUTH2_SECRET = env.str(
    'DJANGO_WEBHOOK_RECEIVER_EDX_OAUTH2_SECRET',
    default='')

WEBHOOK_RECEIVER_SETTINGS = {
    'shopify': {
        'shop_domain': env.str(
            'DJANGO_WEBHOOK_RECEIVER_SETTINGS_SHOPIFY_SHOP_DOMAIN',
            default=''),
        'api_key': env.str(
            'DJANGO_WEBHOOK_RECEIVER_SETTINGS_SHOPIFY_API_KEY',
            default=''),
    },
    'woocommerce': {
        'source': env.str(
            'DJANGO_WEBHOOK_RECEIVER_SETTINGS_WOOCOMMERCE_SOURCE',
            default=''),
        'secret': env.str(
            'DJANGO_WEBHOOK_RECEIVER_SETTINGS_WOOCOMMERCE_SECRET',
            default=''),
    },
}
