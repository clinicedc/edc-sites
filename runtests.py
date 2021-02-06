#!/usr/bin/env python
import logging
import sys
from os.path import abspath, dirname, join

import django
from django.conf import settings
from django.test.runner import DiscoverRunner


class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


base_dir = dirname(abspath(__file__))
app_name = "edc_sites"

installed_apps = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "multisite",
    "edc_sites",
]

DEFAULT_SETTINGS = dict(
    BASE_DIR=base_dir,
    EDC_SITES_MODULE_NAME="edc_sites.tests.sites",
    SITE_ID=10,
    ALLOWED_HOSTS=["localhost"],
    # AUTH_USER_MODEL='custom_user.CustomUser',
    ROOT_URLCONF=f"{app_name}.tests.urls",
    STATIC_URL="/static/",
    INSTALLED_APPS=installed_apps,
    DATABASES={
        # required for tests when acting as a server that deserializes
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": join(base_dir, "db.sqlite3"),
        },
    },
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ]
            },
        }
    ],
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    LANGUAGE_CODE="en-us",
    TIME_ZONE="UTC",
    USE_I18N=True,
    USE_L10N=True,
    USE_TZ=True,
    APP_NAME=app_name,
    EDC_BOOTSTRAP=3,
    DEFAULT_FILE_STORAGE="inmemorystorage.InMemoryStorage",
    MIGRATION_MODULES=DisableMigrations(),
    PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
)


def main():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)
    django.setup()
    tags = [t.split("=")[1] for t in sys.argv if t.startswith("--tag")]
    failures = DiscoverRunner(failfast=False, tags=tags).run_tests([f"{app_name}.tests"])
    sys.exit(failures)


if __name__ == "__main__":
    logging.basicConfig()
    main()
