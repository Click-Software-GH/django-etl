# Migration Guide: YAML Config to Django Settings

This guide helps you migrate from the old YAML-based configuration to the new Django-native settings approach.

!!! warning "Breaking Change"
    Version 2.0+ of the Django ETL Framework uses Django settings instead of YAML files. This change improves Django integration but requires configuration migration.

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
rm etl_config.yaml  # or wherever your config file was
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
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "uhms_new",
        "HOST": "localhost",
        "PORT": 5432,
        "USER": "postgres",
        "PASSWORD": "password",
    },
    "legacy": {
        "ENGINE": "django.db.backends.mysql", 
        "NAME": "uhms_legacy",
        "HOST": "localhost",
        "PORT": 3306,
        "USER": "root",
        "PASSWORD": "password",
    },
}

# ETL-specific configuration
ETL_CONFIG = {
    "PROJECT_NAME": "UHMS-ETL",
    "ENVIRONMENT": "development",
    
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
        'BATCH_SIZE': int(os.environ.get('ETL_BATCH_SIZE', '1000')),
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

## Configuration Mapping

Here's how old YAML settings map to new Django settings:

| YAML Path | Django Setting | Notes |
|-----------|----------------|-------|
| `project_name` | `ETL_CONFIG['PROJECT_NAME']` | Direct mapping |
| `environment` | `ETL_CONFIG['ENVIRONMENT']` | Direct mapping |
| `databases.*` | `DATABASES` | Uses Django's database config |
| `transformation.batch_size` | `ETL_CONFIG['TRANSFORMATION']['BATCH_SIZE']` | Nested structure |
| `logging.level` | `ETL_CONFIG['LOGGING']['LEVEL']` | Nested structure |
| `monitoring.*` | `ETL_CONFIG['MONITORING'][*]` | Nested structure |
| `backup_directory` | `ETL_CONFIG['BACKUP_DIRECTORY']` | Direct mapping |

## Complete Configuration Reference

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

## Testing Your Migration

### 1. Validate Configuration

```python
from django_etl.config import config_manager

# Check for configuration issues
issues = config_manager.validate_config()
if issues:
    for issue in issues:
        print(f"❌ {issue}")
else:
    print("✅ Configuration is valid!")
```

### 2. Test Database Connections

```python
from django.db import connections

for db_name in ['default', 'legacy']:
    try:
        connections[db_name].ensure_connection()
        print(f"✅ Database '{db_name}' connection successful")
    except Exception as e:
        print(f"❌ Database '{db_name}' connection failed: {e}")
```

### 3. Test Transformer Discovery

```python
python manage.py migrate_legacy_data --list
```

## Common Migration Issues

### Issue: "Database not configured"

**Error:**
```
django.core.exceptions.ImproperlyConfigured: Database 'legacy' required by ETL but not configured in DATABASES
```

**Solution:**
Add the database to Django's `DATABASES` setting:

```python
DATABASES = {
    'default': { ... },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'legacy_db',
        # ... other settings
    }
}
```

### Issue: "Transformer not found"

**Error:**
```
No transformers discovered in specified paths
```

**Solution:**
Update transformer discovery paths:

```python
ETL_CONFIG = {
    'TRANSFORMER_DISCOVERY_PATHS': [
        'myapp.transformers',  # Make sure this path is correct
    ],
}
```

### Issue: "Directory permission denied"

**Error:**
```
Cannot create directory '/var/log/etl': Permission denied
```

**Solution:**
Use relative paths or ensure directory permissions:

```python
ETL_CONFIG = {
    'LOG_DIRECTORY': 'logs/etl',  # Relative to BASE_DIR
    'BACKUP_DIRECTORY': 'etl_backups',
}
```

## Benefits of the New Approach

1. **Single Source of Truth** - Database configuration is only in Django's DATABASES
2. **Environment Flexibility** - Use Django's settings patterns for different environments  
3. **Better Error Handling** - Django validates database configurations on startup
4. **Familiar Patterns** - Django developers already know how to work with settings
5. **Integration** - Works seamlessly with Django's connection pooling and routing

## Migration Script

Here's a script to help automate the migration:

```python
#!/usr/bin/env python
"""
Migration script to convert YAML ETL config to Django settings format
"""

import yaml
import json
from pathlib import Path

def convert_yaml_to_django_config(yaml_path):
    """Convert YAML config to Django ETL_CONFIG format"""
    
    with open(yaml_path, 'r') as f:
        yaml_config = yaml.safe_load(f)
    
    # Convert to Django format
    django_config = {
        'PROJECT_NAME': yaml_config.get('project_name', 'ETL Project'),
        'ENVIRONMENT': yaml_config.get('environment', 'development'),
    }
    
    # Transform nested configurations
    if 'transformation' in yaml_config:
        django_config['TRANSFORMATION'] = {
            key.upper(): value 
            for key, value in yaml_config['transformation'].items()
        }
    
    if 'logging' in yaml_config:
        django_config['LOGGING'] = {
            key.upper(): value
            for key, value in yaml_config['logging'].items()
        }
    
    if 'monitoring' in yaml_config:
        django_config['MONITORING'] = {
            key.upper(): value
            for key, value in yaml_config['monitoring'].items()
        }
    
    # Convert databases to Django DATABASES format
    databases = {}
    for db_name, db_config in yaml_config.get('databases', {}).items():
        engine_map = {
            'mysql': 'django.db.backends.mysql',
            'postgresql': 'django.db.backends.postgresql',
            'sqlite': 'django.db.backends.sqlite3',
        }
        
        databases[db_name] = {
            'ENGINE': engine_map.get(db_config.get('engine', 'mysql'), 'django.db.backends.mysql'),
            'NAME': db_config.get('database', ''),
            'HOST': db_config.get('host', 'localhost'),
            'PORT': db_config.get('port', 3306),
            'USER': db_config.get('username', ''),
            'PASSWORD': db_config.get('password', ''),
        }
    
    return django_config, databases

def generate_settings_file(etl_config, databases):
    """Generate Django settings file content"""
    
    settings_content = f'''
# ETL Configuration (migrated from YAML)
DATABASES = {json.dumps(databases, indent=4)}

ETL_CONFIG = {json.dumps(etl_config, indent=4)}
'''
    
    return settings_content

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python migrate_config.py <yaml_config_file>")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    
    try:
        etl_config, databases = convert_yaml_to_django_config(yaml_file)
        settings_content = generate_settings_file(etl_config, databases)
        
        print("# Add this to your Django settings.py:")
        print(settings_content)
        
    except Exception as e:
        print(f"Error converting config: {e}")
        sys.exit(1)
```

## Need Help?

If you encounter issues during migration:

1. Check that your `DATABASES` setting includes all required databases
2. Ensure `ETL_CONFIG` is properly formatted as a Python dictionary
3. Verify that `TRANSFORMER_DISCOVERY_PATHS` point to valid Python modules
4. Run `python manage.py migrate_legacy_data --dry-run` to test configuration

For questions, please:
- [Open an issue](https://github.com/Click-Software-GH/django-etl/issues) on GitHub
- [Start a discussion](https://github.com/Click-Software-GH/django-etl/discussions)
- Email [etl-support@yourcompany.com](mailto:etl-support@yourcompany.com)
