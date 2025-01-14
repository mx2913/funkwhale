"""
Production Configurations

- Use djangosecure
- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send e-mails
- Use Redis on Heroku


"""

from .common import *  # noqa

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env("DJANGO_SECRET_KEY")

# django-secure
# ------------------------------------------------------------------------------
# INSTALLED_APPS += ("djangosecure", )
#
# SECURITY_MIDDLEWARE = (
#     'djangosecure.middleware.SecurityMiddleware',
# )
#
#
# # Make sure djangosecure.middleware.SecurityMiddleware is listed first
# MIDDLEWARE = SECURITY_MIDDLEWARE + MIDDLEWARE
#
# # set this to 60 seconds and then to 518400 when you can prove it works
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
#     "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
# SECURE_FRAME_DENY = env.bool("DJANGO_SECURE_FRAME_DENY", default=True)
# SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
#     "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)
# SECURE_BROWSER_XSS_FILTER = True
# SESSION_COOKIE_SECURE = False
# SESSION_COOKIE_HTTPONLY = True
# SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

# Static Assets
# ------------------------
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# CACHING
# ------------------------------------------------------------------------------
# Heroku URL does not pass the DB number, so we parse it in

# Your production stuff: Below this line define 3rd party library settings
