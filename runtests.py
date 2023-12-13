#!/usr/bin/env python
import logging
from pathlib import Path

from edc_constants.constants import IGNORE
from edc_test_utils import DefaultTestSettings, func_main

app_name = "edc_sites"
base_dir = Path(__file__).absolute().parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    template_dirs=[str(base_dir / app_name / "tests" / "templates")],
    BASE_DIR=base_dir,
    DEBUG=True,
    KEY_PATH=str(base_dir / app_name / "tests" / "etc"),
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    AUTO_CREATE_KEYS=False,
    APP_NAME=app_name,
    SITE_ID=10,
    # LANGUAGES=dict(en="English"),
    EDC_SITES_MODULE_NAME="edc_sites.tests.sites",
    EDC_NAVBAR_VERIFY_ON_LOAD=IGNORE,
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_crypto_fields",
        "edc_auth.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_listboard.apps.AppConfig",
        "edc_navbar.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "multisite",
        "edc_sites",
    ],
    USE_I18N=True,
    USE_L10N=True,
    USE_TZ=True,
    LANGUAGE_CODE="en",
    use_test_urls=True,
    add_dashboard_middleware=True,
).settings


def main():
    tests = ["edc_sites"]
    func_main(project_settings, *tests)


if __name__ == "__main__":
    logging.basicConfig()
    main()
