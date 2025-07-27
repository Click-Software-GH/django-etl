# Migration Guide: YAML Config to Django Settings

This guide helps you migrate from the old YAML-based configuration to the new Django-native settings approach.

## Why This Change?

The Django ETL Framework now uses Django's native settings system instead of separate YAML files. This provides:

- ✅ **Better Django Integration** - Uses Django's built-in database configuration
- ✅ **Familiar Patterns** - Django developers already know this approach
- ✅ **Environment Variables** - Easy to use with Django's environment variable support
- ✅ **Less Configuration** - No need to duplicate database settings
- ✅ **Better Validation** - Leverages Django's configuration validation

## Migration Steps

### 1. Remove Old Configuration Files

If you have existing YAML configuration files, you can remove them:

```bash
rm -rf django_etl/config/
```

### 2. Update Your Django Settings

**Before (YAML config):**
```yaml
# etl_config.yaml
project_name: UHMS-ETL
environment: development
databases:
  legacy:
    host: localhost
    port: 3306
    database: uhms_legacy
    username: root
    password: password
    engine: mysql
  target:
    host: localhost
    port: 5432
    database: uhms_new
    username: postgres
    password: password
    engine: postgresql
transformation:
  batch_size: 1000
  enable_validation: true
  max_retries: 3
logging:
  level: INFO
  console_output: true
monitoring:
  enable_profiling: true
  enable_metrics: true
```

**After (Django settings):**
```python
# settings.py

# Use Django's native database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uhms_new',
        'HOST': 'localhost',
        'PORT': 5432,
        'USER': 'postgres',
        'PASSWORD': 'password',
    },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'uhms_legacy',
        'HOST': 'localhost',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'password',
    }
}

# ETL-specific configuration
ETL_CONFIG = {
    'PROJECT_NAME': 'UHMS-ETL',
    'ENVIRONMENT': 'development',
    
    'TRANSFORMATION': {
        'BATCH_SIZE': 1000,
        'ENABLE_VALIDATION': True,
        'MAX_RETRIES': 3,
    },
    
    'LOGGING': {
        'LEVEL': 'INFO',
        'CONSOLE_OUTPUT': True,
    },
    
    'MONITORING': {
        'ENABLE_PROFILING': True,
        'ENABLE_METRICS': True,
    },
    
    'REQUIRED_DATABASES': ['default', 'legacy'],
}
```

### 3. Update Your Code

**Before:**
```python
from django_etl.config import config_manager

# Get database config
db_config = config_manager.get_database_config('legacy')
connection_string = f"mysql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
```

**After:**
```python
from django_etl.config import config_manager
from django.db import connections

# Get database config (now from Django DATABASES)
db_config = config_manager.get_database_config('legacy')
# Or use Django's connection directly
legacy_connection = connections['legacy']
```

### 4. Environment Variables

**Before (YAML with environment variables):**
```yaml
databases:
  legacy:
    host: ${LEGACY_DB_HOST}
    password: ${LEGACY_DB_PASSWORD}
```

**After (Django settings with environment variables):**
```python
import os

DATABASES = {
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ.get('LEGACY_DB_HOST', 'localhost'),
        'PASSWORD': os.environ.get('LEGACY_DB_PASSWORD'),
    }
}

ETL_CONFIG = {
    'TRANSFORMATION': {
        'BATCH_SIZE': int(os.environ.get('ETL_BATCH_SIZE', 1000)),
    },
}
```

### 5. Different Environments

**Before (separate YAML files):**
```
config/
  etl_config_dev.yaml
  etl_config_staging.yaml  
  etl_config_prod.yaml
```

**After (Django settings patterns):**
```python
# settings/base.py
ETL_CONFIG = {
    'TRANSFORMATION': {
        'BATCH_SIZE': 1000,
    },
}

# settings/production.py
from .base import *

ETL_CONFIG.update({
    'TRANSFORMATION': {
        'BATCH_SIZE': 5000,  # Larger batches in production
    },
    'MONITORING': {
        'ALERT_EMAIL': 'admin@company.com',
    },
})
```

## Configuration Reference

### Complete ETL_CONFIG Options

```python
ETL_CONFIG = {
    # Project settings
    'PROJECT_NAME': 'Your-ETL-Project',
    'ENVIRONMENT': 'development',  # development, staging, production
    
    # Transformation settings
    'TRANSFORMATION': {
        'BATCH_SIZE': 1000,
        'MAX_RETRIES': 3,
        'RETRY_DELAY': 5,
        'ENABLE_VALIDATION': True,
        'VALIDATION_MODE': 'strict',  # strict, lenient, warning_only
        'CLEANUP_ON_ERROR': True,
        'PARALLEL_PROCESSING': False,
        'MAX_WORKERS': 4,
    },
    
    # Logging settings
    'LOGGING': {
        'LEVEL': 'INFO',
        'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'FILE_PATH': None,  # Will use LOG_DIRECTORY/etl.log
        'MAX_FILE_SIZE_MB': 100,
        'BACKUP_COUNT': 5,
        'CONSOLE_OUTPUT': True,
    },
    
    # Monitoring settings
    'MONITORING': {
        'ENABLE_PROFILING': True,
        'ENABLE_METRICS': True,
        'ALERT_ON_ERRORS': True,
        'ALERT_EMAIL': None,
        'WEBHOOK_URL': None,
        'SLACK_CHANNEL': None,
    },
    
    # Directory settings (relative to BASE_DIR)
    'BACKUP_DIRECTORY': 'etl_backups',
    'TEMP_DIRECTORY': 'etl_temp',
    'LOG_DIRECTORY': 'logs/etl',
    
    # Feature flags
    'ENABLE_ROLLBACK': True,
    'ENABLE_DRY_RUN': True,
    'ENABLE_PARALLEL_TRANSFORMS': False,
    
    # Transformer discovery
    'TRANSFORMER_DISCOVERY_PATHS': [
        'myapp.transformers',
    ],
    
    # Required databases (must exist in DATABASES)
    'REQUIRED_DATABASES': ['default'],
}
```

## Benefits of the New Approach

1. **Single Source of Truth** - Database configuration is only in Django's DATABASES
2. **Environment Flexibility** - Use Django's settings patterns for different environments
3. **Better Error Handling** - Django validates database configurations on startup
4. **Familiar Patterns** - Django developers already know how to work with settings
5. **Integration** - Works seamlessly with Django's connection pooling and routing

## Need Help?

If you encounter issues during migration:

1. Check that your `DATABASES` setting includes all required databases
2. Ensure `ETL_CONFIG` is properly formatted as a Python dictionary
3. Verify that `TRANSFORMER_DISCOVERY_PATHS` point to valid Python modules
4. Run `python manage.py migrate_legacy_data --dry-run` to test configuration

For questions, please open an issue on GitHub or start a discussion.
