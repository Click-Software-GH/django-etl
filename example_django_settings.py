# Example Django project settings.py configuration for ETL Framework
"""
Add this configuration to your Django project's settings.py to configure the ETL framework
"""

# Your existing Django settings...
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "uhms_new",
        "HOST": "localhost",
        "PORT": 5432,
        "USER": "postgres",
        "PASSWORD": "password",
        "OPTIONS": {
            "charset": "utf8",
        },
    },
    "legacy": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "uhms_legacy",
        "HOST": "localhost",
        "PORT": 3306,
        "USER": "root",
        "PASSWORD": "password",
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    },
}

# ETL Framework Configuration
ETL_CONFIG = {
    "PROJECT_NAME": "UHMS-ETL",
    "ENVIRONMENT": "development",  # development, staging, production
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
        "FILE_PATH": None,  # Will use LOG_DIRECTORY/etl.log
        "MAX_FILE_SIZE_MB": 100,
        "BACKUP_COUNT": 5,
        "CONSOLE_OUTPUT": True,
    },
    # Monitoring settings
    "MONITORING": {
        "ENABLE_PROFILING": True,
        "ENABLE_METRICS": True,
        "ALERT_ON_ERRORS": True,
        "ALERT_EMAIL": "admin@example.com",
        "WEBHOOK_URL": None,
        "SLACK_CHANNEL": "#etl-alerts",
    },
    # Directory settings (relative to BASE_DIR)
    "BACKUP_DIRECTORY": "etl_backups",
    "TEMP_DIRECTORY": "etl_temp",
    "LOG_DIRECTORY": "logs/etl",
    # Feature flags
    "ENABLE_ROLLBACK": True,
    "ENABLE_DRY_RUN": True,
    "ENABLE_PARALLEL_TRANSFORMS": False,
    # Transformer discovery paths
    "TRANSFORMER_DISCOVERY_PATHS": [
        "myapp.transformers",
        "healthcare.etl.transformers",
    ],
    # Required databases (must exist in DATABASES setting)
    "REQUIRED_DATABASES": ["default", "legacy"],
}

# Add django_etl to your INSTALLED_APPS
INSTALLED_APPS = [
    # ... your existing apps
    "django_etl",
]
