# django_etl_framework/django_etl/settings.py
"""
Django ETL Framework Settings

These settings can be overridden in your Django project's settings.py by defining ETL_CONFIG
"""

from django.conf import settings
import os

# Default ETL configuration
DEFAULT_ETL_CONFIG = {
    "PROJECT_NAME": "Django-ETL",
    "ENVIRONMENT": "development",
    # Transformation settings
    "TRANSFORMATION": {
        "BATCH_SIZE": 1000,
        "MAX_RETRIES": 3,
        "RETRY_DELAY": 5,
        "ENABLE_VALIDATION": True,
        "VALIDATION_MODE": "strict",  # strict, lenient, warning_only
        "CLEANUP_ON_ERROR": True,
        "PARALLEL_PROCESSING": False,
        "MAX_WORKERS": 4,
    },
    # Logging settings
    "LOGGING": {
        "LEVEL": "INFO",
        "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "FILE_PATH": None,  # Will default to log_directory/etl.log
        "MAX_FILE_SIZE_MB": 100,
        "BACKUP_COUNT": 5,
        "CONSOLE_OUTPUT": True,
    },
    # Monitoring settings
    "MONITORING": {
        "ENABLE_PROFILING": True,
        "ENABLE_METRICS": True,
        "ALERT_ON_ERRORS": True,
        "ALERT_EMAIL": None,
        "WEBHOOK_URL": None,
        "SLACK_CHANNEL": None,
    },
    # Directory settings (will use BASE_DIR if available)
    "BACKUP_DIRECTORY": "/tmp/etl_backups",
    "TEMP_DIRECTORY": "/tmp/etl_temp",
    "LOG_DIRECTORY": "/tmp/etl_logs",
    # Feature flags
    "ENABLE_ROLLBACK": True,
    "ENABLE_DRY_RUN": True,
    "ENABLE_PARALLEL_TRANSFORMS": False,
    # Transformer discovery
    "TRANSFORMER_DISCOVERY_PATHS": [],
    # Required databases (will validate these exist in Django DATABASES)
    "REQUIRED_DATABASES": ["default"],
}


# Get user configuration from Django settings
def get_etl_setting(name, default=None):
    """Get ETL setting from Django settings with fallback to defaults"""
    etl_settings = getattr(settings, "ETL_CONFIG", {})

    if name in etl_settings:
        return etl_settings[name]

    if name in DEFAULT_ETL_CONFIG:
        return DEFAULT_ETL_CONFIG[name]

    return default


# Commonly used settings for backward compatibility
BATCH_SIZE = get_etl_setting("TRANSFORMATION", {}).get("BATCH_SIZE", 1000)
MAX_RETRIES = get_etl_setting("TRANSFORMATION", {}).get("MAX_RETRIES", 3)
RETRY_DELAY = get_etl_setting("TRANSFORMATION", {}).get("RETRY_DELAY", 5)
ENABLE_VALIDATION = get_etl_setting("TRANSFORMATION", {}).get("ENABLE_VALIDATION", True)
VALIDATION_MODE = get_etl_setting("TRANSFORMATION", {}).get("VALIDATION_MODE", "strict")
ENABLE_PROFILING = get_etl_setting("MONITORING", {}).get("ENABLE_PROFILING", True)
ENABLE_ROLLBACK = get_etl_setting("ENABLE_ROLLBACK", True)
BACKUP_DIRECTORY = get_etl_setting("BACKUP_DIRECTORY", "/tmp/etl_backups")
LOG_LEVEL = get_etl_setting("LOGGING", {}).get("LEVEL", "INFO")
DEFAULT_LEGACY_DB = get_etl_setting("DEFAULT_LEGACY_DB", "legacy")
