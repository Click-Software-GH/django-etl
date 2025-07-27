# django_etl_framework/django_etl/settings.py
"""
Django ETL Framework Settings

These settings can be overridden in your Django project's settings.py
"""

from django.conf import settings
import os

# Default ETL configuration
DEFAULT_ETL_CONFIG = {
    "BATCH_SIZE": 1000,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 5,
    "ENABLE_VALIDATION": True,
    "VALIDATION_MODE": "strict",  # strict, lenient, warning_only
    "ENABLE_PROFILING": True,
    "ENABLE_ROLLBACK": True,
    "BACKUP_DIRECTORY": "/tmp/etl_backups",
    "LOG_LEVEL": "INFO",
    "DEFAULT_LEGACY_DB": "legacy",
}


# Get user configuration from Django settings
def get_etl_setting(name, default=None):
    """Get ETL setting from Django settings with fallback to defaults"""
    etl_settings = getattr(settings, "ETL_FRAMEWORK", {})

    if name in etl_settings:
        return etl_settings[name]

    if name in DEFAULT_ETL_CONFIG:
        return DEFAULT_ETL_CONFIG[name]

    return default


# Commonly used settings
BATCH_SIZE = get_etl_setting("BATCH_SIZE")
MAX_RETRIES = get_etl_setting("MAX_RETRIES")
RETRY_DELAY = get_etl_setting("RETRY_DELAY")
ENABLE_VALIDATION = get_etl_setting("ENABLE_VALIDATION")
VALIDATION_MODE = get_etl_setting("VALIDATION_MODE")
ENABLE_PROFILING = get_etl_setting("ENABLE_PROFILING")
ENABLE_ROLLBACK = get_etl_setting("ENABLE_ROLLBACK")
BACKUP_DIRECTORY = get_etl_setting("BACKUP_DIRECTORY")
LOG_LEVEL = get_etl_setting("LOG_LEVEL")
DEFAULT_LEGACY_DB = get_etl_setting("DEFAULT_LEGACY_DB")
