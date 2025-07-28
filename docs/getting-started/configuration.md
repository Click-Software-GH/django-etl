# Configuration

Configure the Django ETL Framework to work with your Django project and databases.

## Django Settings Integration

The framework integrates seamlessly with Django's settings system. All configuration is done through your Django project's `settings.py` file.

## Basic Configuration

### Minimal Setup

```python
# settings.py
INSTALLED_APPS = [
    # ... your apps
    "django_etl",
]

# Minimal ETL configuration
ETL_CONFIG = {
    "PROJECT_NAME": "My ETL Project",
}
```

### Complete Configuration

```python
# settings.py
ETL_CONFIG = {
    # Project settings
    "PROJECT_NAME": "Healthcare ETL System",
    "ENVIRONMENT": "production",  # development, staging, production
    
    # Transformation settings
    "TRANSFORMATION": {
        "BATCH_SIZE": 2000,
        "MAX_RETRIES": 5,
        "RETRY_DELAY": 10,
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
        "ALERT_EMAIL": "admin@healthcare.com",
        "WEBHOOK_URL": "https://hooks.slack.com/services/...",
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
    
    # Transformer discovery
    "TRANSFORMER_DISCOVERY_PATHS": [
        "myapp.transformers",
        "healthcare.etl.transformers",
    ],
    
    # Required databases (must exist in DATABASES)
    "REQUIRED_DATABASES": ["default", "legacy", "analytics"],
}
```

## Database Configuration

The ETL framework uses Django's built-in `DATABASES` setting. No separate database configuration needed!

### Example Multi-Database Setup

```python
# settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "healthcare_new",
        "HOST": "localhost",
        "PORT": 5432,
        "USER": "postgres",
        "PASSWORD": "secure_password",
        "OPTIONS": {
            "charset": "utf8",
        },
    },
    "legacy": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "old_hospital_system",
        "HOST": "192.168.1.100",
        "PORT": 3306,
        "USER": "migration_user",
        "PASSWORD": "migration_pass",
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    },
    "analytics": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "analytics.sqlite3",
    },
}
```

## Environment-Specific Configuration

### Using Environment Variables

```python
# settings.py
import os


ETL_CONFIG = {
    "PROJECT_NAME": os.environ.get("ETL_PROJECT_NAME", "Default ETL"),
    "ENVIRONMENT": os.environ.get("DJANGO_ENV", "development"),
    
    "TRANSFORMATION": {
        "BATCH_SIZE": int(os.environ.get("ETL_BATCH_SIZE", 1000)),
        "ENABLE_VALIDATION": os.environ.get("ETL_VALIDATION", "true").lower() == "true",
    },
    
    'MONITORING': {
        'ALERT_EMAIL': os.environ.get('ETL_ALERT_EMAIL'),
        'SLACK_CHANNEL': os.environ.get('ETL_SLACK_CHANNEL'),
    },
}
```

### Development vs Production

#### Development Settings

```python
# settings/development.py
from .base import *

ETL_CONFIG = {
    'PROJECT_NAME': 'Healthcare ETL (Dev)',
    'ENVIRONMENT': 'development',
    
    'TRANSFORMATION': {
        'BATCH_SIZE': 100,  # Smaller batches for testing
        'VALIDATION_MODE': 'lenient',
    },
    
    'LOGGING': {
        'LEVEL': 'DEBUG',
        'CONSOLE_OUTPUT': True,
    },
    
    'MONITORING': {
        'ENABLE_PROFILING': True,
        'ALERT_ON_ERRORS': False,  # No alerts in dev
    },
}
```

#### Production Settings

```python
# settings/production.py
from .base import *

ETL_CONFIG = {
    'PROJECT_NAME': 'Healthcare ETL (Production)',
    'ENVIRONMENT': 'production',
    
    'TRANSFORMATION': {
        'BATCH_SIZE': 5000,  # Larger batches for performance
        'VALIDATION_MODE': 'strict',
        'PARALLEL_PROCESSING': True,
        'MAX_WORKERS': 8,
    },
    
    'LOGGING': {
        'LEVEL': 'INFO',
        'CONSOLE_OUTPUT': False,
        'FILE_PATH': '/var/log/etl/production.log',
    },
    
    'MONITORING': {
        'ENABLE_PROFILING': True,
        'ENABLE_METRICS': True,
        'ALERT_ON_ERRORS': True,
        'ALERT_EMAIL': 'ops@healthcare.com',
    },
    
    'BACKUP_DIRECTORY': '/opt/etl/backups',
    'LOG_DIRECTORY': '/var/log/etl',
}
```

## Configuration Reference

### Transformation Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `BATCH_SIZE` | int | 1000 | Number of records to process in each batch |
| `MAX_RETRIES` | int | 3 | Maximum number of retry attempts for failed operations |
| `RETRY_DELAY` | int | 5 | Delay in seconds between retry attempts |
| `ENABLE_VALIDATION` | bool | True | Enable data validation during transformation |
| `VALIDATION_MODE` | str | "strict" | Validation strictness: strict, lenient, warning_only |
| `CLEANUP_ON_ERROR` | bool | True | Clean up temporary data on errors |
| `PARALLEL_PROCESSING` | bool | False | Enable parallel processing of batches |
| `MAX_WORKERS` | int | 4 | Maximum number of worker processes |

### Logging Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `LEVEL` | str | "INFO" | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `FORMAT` | str | Standard format | Log message format string |
| `FILE_PATH` | str | None | Specific log file path (overrides LOG_DIRECTORY) |
| `MAX_FILE_SIZE_MB` | int | 100 | Maximum log file size before rotation |
| `BACKUP_COUNT` | int | 5 | Number of backup log files to keep |
| `CONSOLE_OUTPUT` | bool | True | Enable console logging |

### Monitoring Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ENABLE_PROFILING` | bool | True | Enable performance profiling |
| `ENABLE_METRICS` | bool | True | Enable metrics collection |
| `ALERT_ON_ERRORS` | bool | True | Send alerts when errors occur |
| `ALERT_EMAIL` | str | None | Email address for alerts |
| `WEBHOOK_URL` | str | None | Webhook URL for notifications |
| `SLACK_CHANNEL` | str | None | Slack channel for alerts |

### Directory Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `BACKUP_DIRECTORY` | str | "/tmp/etl_backups" | Directory for data backups |
| `TEMP_DIRECTORY` | str | "/tmp/etl_temp" | Directory for temporary files |
| `LOG_DIRECTORY` | str | "/tmp/etl_logs" | Directory for log files |

!!! tip "Path Resolution"
    
    Directory paths are resolved relative to Django's `BASE_DIR` if they don't start with `/`.

## Validation and Testing

### Validate Configuration

```python
from django_etl.config import config_manager

# Check for configuration issues
issues = config_manager.validate_config()
if issues:
    for issue in issues:
        print(f"Configuration issue: {issue}")
else:
    print("Configuration is valid!")
```

### Test Database Connections

```python
from django.db import connections

# Test all configured databases
for db_name in connections:
    try:
        connections[db_name].ensure_connection()
        print(f"✓ Database '{db_name}' connection successful")
    except Exception as e:
        print(f"✗ Database '{db_name}' connection failed: {e}")
```

## Migration from YAML

If you're migrating from the old YAML-based configuration, see our [Migration Guide](../migration-guide.md) for detailed instructions.

## Next Steps

- [Quick Start Guide](quickstart.md) - Create your first transformer
- [Database Configuration](../user-guide/databases.md) - Advanced database setup
- [Management Commands](../user-guide/commands.md) - Learn about available commands
