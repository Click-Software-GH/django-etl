# Configuration API

The Django ETL Framework provides a comprehensive configuration system that integrates seamlessly with Django's settings. This page documents all available configuration options and how to use them.

## Configuration Overview

All ETL configuration is done through your Django project's `settings.py` file using the `ETL_CONFIG` dictionary. The framework provides sensible defaults for all settings, so you only need to specify what you want to change.

## Basic Configuration

### Minimal Setup

```python
# settings.py
ETL_CONFIG = {
    'PROJECT_NAME': 'My ETL Project',
}
```

### Common Configuration

```python
# settings.py
ETL_CONFIG = {
    'PROJECT_NAME': 'Healthcare Data Migration',
    'ENVIRONMENT': 'production',
    
    'TRANSFORMATION': {
        'BATCH_SIZE': 2000,
        'ENABLE_VALIDATION': True,
        'VALIDATION_MODE': 'strict',
    },
    
    'MONITORING': {
        'ENABLE_PROFILING': True,
        'ALERT_EMAIL': 'admin@hospital.com',
    },
    
    'REQUIRED_DATABASES': ['default', 'legacy'],
}
```

## Configuration Reference

### Project Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `PROJECT_NAME` | string | "Django-ETL" | Name of your ETL project (appears in logs and reports) |
| `ENVIRONMENT` | string | "development" | Environment name: `development`, `staging`, or `production` |

**Example:**
```python
ETL_CONFIG = {
    'PROJECT_NAME': 'Hospital Data Migration',
    'ENVIRONMENT': 'production',
}
```

### Transformation Settings

Configure how data processing behaves:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `BATCH_SIZE` | int | 1000 | Number of records to process in each batch |
| `MAX_RETRIES` | int | 3 | Maximum retry attempts for failed operations |
| `RETRY_DELAY` | int | 5 | Seconds to wait between retry attempts |
| `ENABLE_VALIDATION` | bool | True | Enable data validation during transformation |
| `VALIDATION_MODE` | string | "strict" | Validation behavior: `strict`, `lenient`, or `warning_only` |
| `CLEANUP_ON_ERROR` | bool | True | Automatically clean up temporary data on errors |
| `PARALLEL_PROCESSING` | bool | False | Enable parallel processing of batches |
| `MAX_WORKERS` | int | 4 | Maximum number of parallel worker processes |

**Example:**
```python
ETL_CONFIG = {
    'TRANSFORMATION': {
        'BATCH_SIZE': 2000,         # Process 2000 records at a time
        'MAX_RETRIES': 5,           # Retry failed operations up to 5 times
        'ENABLE_VALIDATION': True,  # Validate all data
        'VALIDATION_MODE': 'strict', # Fail on any validation error
        'PARALLEL_PROCESSING': True, # Use multiple CPU cores
        'MAX_WORKERS': 8,           # Use up to 8 worker processes
    }
}
```

**Validation Modes:**
- **`strict`**: Stop processing on any validation error
- **`lenient`**: Log validation errors but continue processing
- **`warning_only`**: Only log warnings, never fail validation

### Logging Settings

Control how ETL operations are logged:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `LEVEL` | string | "INFO" | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `FORMAT` | string | Standard format | Python logging format string |
| `FILE_PATH` | string | None | Specific log file path (overrides LOG_DIRECTORY) |
| `MAX_FILE_SIZE_MB` | int | 100 | Maximum log file size before rotation |
| `BACKUP_COUNT` | int | 5 | Number of backup log files to keep |
| `CONSOLE_OUTPUT` | bool | True | Enable console logging output |

**Example:**
```python
ETL_CONFIG = {
    'LOGGING': {
        'LEVEL': 'DEBUG',                    # Show all log messages
        'FILE_PATH': '/var/log/etl/migration.log',  # Specific log file
        'MAX_FILE_SIZE_MB': 50,              # Rotate at 50MB
        'BACKUP_COUNT': 10,                  # Keep 10 backup files
        'CONSOLE_OUTPUT': False,             # Disable console logging
    }
}
```

### Monitoring Settings

Configure performance monitoring and alerts:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ENABLE_PROFILING` | bool | True | Enable performance profiling |
| `ENABLE_METRICS` | bool | True | Enable metrics collection |
| `ALERT_ON_ERRORS` | bool | True | Send alerts when errors occur |
| `ALERT_EMAIL` | string | None | Email address for error alerts |
| `WEBHOOK_URL` | string | None | Webhook URL for notifications |
| `SLACK_CHANNEL` | string | None | Slack channel for alerts |

**Example:**
```python
ETL_CONFIG = {
    'MONITORING': {
        'ENABLE_PROFILING': True,
        'ENABLE_METRICS': True,
        'ALERT_ON_ERRORS': True,
        'ALERT_EMAIL': 'etl-alerts@hospital.com',
        'SLACK_CHANNEL': '#data-migration-alerts',
        'WEBHOOK_URL': 'https://hooks.slack.com/services/...',
    }
}
```

### Directory Settings

Configure where files are stored:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `BACKUP_DIRECTORY` | string | "/tmp/etl_backups" | Directory for data backups |
| `TEMP_DIRECTORY` | string | "/tmp/etl_temp" | Directory for temporary files |
| `LOG_DIRECTORY` | string | "/tmp/etl_logs" | Directory for log files |

**Example:**
```python
ETL_CONFIG = {
    'BACKUP_DIRECTORY': '/opt/etl/backups',
    'TEMP_DIRECTORY': '/opt/etl/temp',
    'LOG_DIRECTORY': '/var/log/etl',
}
```

!!! note "Path Resolution"
    Directory paths are resolved relative to Django's `BASE_DIR` if they don't start with `/`.

### Feature Flags

Enable or disable framework features:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ENABLE_ROLLBACK` | bool | True | Enable rollback functionality |
| `ENABLE_DRY_RUN` | bool | True | Enable dry-run mode |
| `ENABLE_PARALLEL_TRANSFORMS` | bool | False | Enable parallel transformer execution |

**Example:**
```python
ETL_CONFIG = {
    'ENABLE_ROLLBACK': True,            # Allow rollbacks
    'ENABLE_DRY_RUN': True,            # Allow testing without changes
    'ENABLE_PARALLEL_TRANSFORMS': False, # Disable parallel transformers
}
```

### Transformer Discovery

Configure how the framework finds your transformers:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `TRANSFORMER_DISCOVERY_PATHS` | list | [] | Python module paths to search for transformers |
| `REQUIRED_DATABASES` | list | ["default"] | Databases that must be configured |

**Example:**
```python
ETL_CONFIG = {
    'TRANSFORMER_DISCOVERY_PATHS': [
        'myapp.transformers',           # Look in myapp.transformers module
        'healthcare.etl.transformers',  # Look in healthcare.etl.transformers
        'data.migration',               # Look in data.migration module
    ],
    'REQUIRED_DATABASES': [
        'default',                      # Default Django database
        'legacy',                       # Legacy system database
        'analytics',                    # Analytics database
    ],
}
```

## Database Configuration

The ETL framework uses Django's built-in `DATABASES` setting. Configure your databases in Django's standard way:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'new_system',
        'HOST': 'localhost',
        'PORT': 5432,
        'USER': 'postgres',
        'PASSWORD': 'password',
    },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'old_system',
        'HOST': '192.168.1.100',
        'PORT': 3306,
        'USER': 'migration_user',
        'PASSWORD': 'migration_password',
    }
}
```

## Environment-Specific Configuration

### Using Environment Variables

```python
import os

ETL_CONFIG = {
    'PROJECT_NAME': os.environ.get('ETL_PROJECT_NAME', 'Default ETL'),
    'ENVIRONMENT': os.environ.get('DJANGO_ENV', 'development'),
    
    'TRANSFORMATION': {
        'BATCH_SIZE': int(os.environ.get('ETL_BATCH_SIZE', '1000')),
    },
    
    'MONITORING': {
        'ALERT_EMAIL': os.environ.get('ETL_ALERT_EMAIL'),
    },
}
```

### Different Settings Per Environment

**Development:**
```python
# settings/development.py
ETL_CONFIG = {
    'TRANSFORMATION': {
        'BATCH_SIZE': 100,              # Smaller batches for testing
        'VALIDATION_MODE': 'lenient',   # More forgiving validation
    },
    'LOGGING': {
        'LEVEL': 'DEBUG',               # Verbose logging
        'CONSOLE_OUTPUT': True,         # Show logs in console
    },
    'MONITORING': {
        'ALERT_ON_ERRORS': False,       # No alerts in development
    },
}
```

**Production:**
```python
# settings/production.py
ETL_CONFIG = {
    'TRANSFORMATION': {
        'BATCH_SIZE': 5000,             # Larger batches for performance
        'VALIDATION_MODE': 'strict',    # Strict validation
        'PARALLEL_PROCESSING': True,    # Use multiple cores
        'MAX_WORKERS': 16,              # More workers
    },
    'LOGGING': {
        'LEVEL': 'INFO',                # Less verbose logging
        'CONSOLE_OUTPUT': False,        # File logging only
        'FILE_PATH': '/var/log/etl/production.log',
    },
    'MONITORING': {
        'ALERT_ON_ERRORS': True,        # Enable alerts
        'ALERT_EMAIL': 'ops@company.com',
    },
}
```

## Configuration Validation

The framework automatically validates your configuration when Django starts. Common validation errors:

### Missing Required Database

**Error:** `Database 'legacy' required by ETL but not configured in DATABASES`

**Solution:** Add the database to your `DATABASES` setting:
```python
DATABASES = {
    'default': { ... },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'legacy_system',
        # ... other settings
    }
}
```

### Invalid Directory Permissions

**Error:** `Cannot create directory '/var/log/etl': Permission denied`

**Solution:** Use relative paths or ensure proper permissions:
```python
ETL_CONFIG = {
    'LOG_DIRECTORY': 'logs/etl',  # Relative to BASE_DIR
}
```

### Invalid Transformer Paths

**Error:** `No transformers found in myapp.transformers`

**Solution:** Ensure the module exists and contains transformer classes:
```python
# Check that myapp/transformers/__init__.py exists
# and contains transformer classes that inherit from BaseTransformer
```

## Testing Your Configuration

```python
# Test in Django shell
python manage.py shell

>>> from django_etl.config import config_manager
>>> issues = config_manager.validate_config()
>>> if issues:
...     for issue in issues:
...         print(f"❌ {issue}")
... else:
...     print("✅ Configuration is valid!")
```

## Complete Example

Here's a complete configuration example for a healthcare system:

```python
# settings.py
import os

# Django databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'healthcare_new',
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': int(os.environ.get('DB_PORT', '5432')),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
    },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hospital_legacy',
        'HOST': os.environ.get('LEGACY_DB_HOST', '192.168.1.100'),
        'PORT': int(os.environ.get('LEGACY_DB_PORT', '3306')),
        'USER': os.environ.get('LEGACY_DB_USER', 'migration'),
        'PASSWORD': os.environ.get('LEGACY_DB_PASSWORD'),
    }
}

# ETL Configuration
ETL_CONFIG = {
    # Project identification
    'PROJECT_NAME': 'Healthcare Data Migration',
    'ENVIRONMENT': os.environ.get('DJANGO_ENV', 'development'),
    
    # Data processing settings
    'TRANSFORMATION': {
        'BATCH_SIZE': int(os.environ.get('ETL_BATCH_SIZE', '2000')),
        'MAX_RETRIES': 5,
        'RETRY_DELAY': 10,
        'ENABLE_VALIDATION': True,
        'VALIDATION_MODE': 'strict',
        'CLEANUP_ON_ERROR': True,
        'PARALLEL_PROCESSING': True,
        'MAX_WORKERS': 8,
    },
    
    # Logging configuration
    'LOGGING': {
        'LEVEL': 'INFO',
        'FILE_PATH': '/var/log/etl/migration.log',
        'MAX_FILE_SIZE_MB': 100,
        'BACKUP_COUNT': 10,
        'CONSOLE_OUTPUT': True,
    },
    
    # Monitoring and alerts
    'MONITORING': {
        'ENABLE_PROFILING': True,
        'ENABLE_METRICS': True,
        'ALERT_ON_ERRORS': True,
        'ALERT_EMAIL': os.environ.get('ETL_ALERT_EMAIL'),
        'SLACK_CHANNEL': '#data-migration',
    },
    
    # File storage
    'BACKUP_DIRECTORY': '/opt/etl/backups',
    'TEMP_DIRECTORY': '/opt/etl/temp',
    'LOG_DIRECTORY': '/var/log/etl',
    
    # Feature flags
    'ENABLE_ROLLBACK': True,
    'ENABLE_DRY_RUN': True,
    'ENABLE_PARALLEL_TRANSFORMS': False,
    
    # Transformer discovery
    'TRANSFORMER_DISCOVERY_PATHS': [
        'healthcare.transformers.patients',
        'healthcare.transformers.appointments',
        'healthcare.transformers.billing',
        'healthcare.transformers.medical_records',
    ],
    
    # Required databases
    'REQUIRED_DATABASES': ['default', 'legacy'],
}
```

This comprehensive configuration provides a solid foundation for healthcare data migration projects, with proper error handling, monitoring, and performance optimization.
