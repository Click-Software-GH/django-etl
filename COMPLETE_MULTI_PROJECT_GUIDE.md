# Django ETL Framework - Complete Multi-Project Usage Guide

## 🚀 **Complete Integration Guide**

This guide covers how to use the Django ETL Framework across multiple Django projects with all the existing components from your UHMS project.

## 📦 **Installation Options**

### **Option 1: Editable Installation (Recommended for Development)**

This installs the package in "editable" mode, meaning any changes you make to the source code are immediately reflected:

```bash
# From the django_etl_framework directory
cd /path/to/django_etl_framework
pip install -e .

# Or from anywhere, pointing to the directory
pip install -e /path/to/django_etl_framework
```

**Benefits:**
- ✅ Changes to source code take effect immediately
- ✅ Perfect for development and customization
- ✅ Can modify and extend the framework

### **Option 2: Standard Installation from Source**

Install as a regular package (changes require reinstallation):

```bash
cd /path/to/django_etl_framework
pip install .
```

### **Option 3: Install from Git Repository**

If you've pushed the framework to a Git repository:

```bash
# Install from Git (replace with your repository URL)
pip install git+https://github.com/yourusername/django-etl-framework.git

# Install specific branch or tag
pip install git+https://github.com/yourusername/django-etl-framework.git@main
pip install git+https://github.com/yourusername/django-etl-framework.git@v1.0.0
```

### **Option 4: Install with Extra Dependencies**

Install with additional optional features:

```bash
# For enhanced database support
pip install -e .[database]

# For development tools
pip install -e .[dev]

# For documentation tools  
pip install -e .[docs]

# For monitoring capabilities
pip install -e .[monitoring]

# For async support
pip install -e .[async]

# Install everything
pip install -e .[database,dev,docs,monitoring,async]
```

### **Option 5: Create a Wheel for Distribution**

Create a distributable package:

```bash
# Install build tools
pip install build

# Create wheel
cd /path/to/django_etl_framework
python -m build

# Install the wheel
pip install dist/django_etl_framework-1.0.0-py3-none-any.whl
```

### **Option 6: Install from PyPI (Future)**

When published to PyPI:

```bash
pip install django-etl-framework

# With extras
pip install django-etl-framework[database,dev]
```

## 🔧 **Verification**

After installation, verify it works:

```python
# Test basic import
import django_etl
print(f"Django ETL Framework v{django_etl.__version__} installed successfully!")

# Test main components
from django_etl import BaseTransformer
from django_etl.discovery import discover_transformers
from django_etl.models import MigrationLog

print("✅ All core components imported successfully")
```

## 🗂️ **Package Location**

Check where the package is installed:

```bash
pip show django-etl-framework
```

For editable installs, you'll see:
- **Location**: Your virtual environment's site-packages
- **Editable project location**: Your source directory

## 💡 **Best Practices for Virtual Environments**

### **Create a Dedicated Virtual Environment**

```bash
# Create a new virtual environment for your project
python -m venv myproject_env

# Activate it
source myproject_env/bin/activate  # Linux/Mac
# or 
myproject_env\Scripts\activate  # Windows

# Install the ETL framework
pip install -e /path/to/django_etl_framework
```

### **Requirements File**

Create a `requirements.txt` for your project:

```txt
# requirements.txt

# Core Django
Django>=3.2,<5.0

# ETL Framework (editable install)
-e /path/to/django_etl_framework

# Or from Git
# -e git+https://github.com/yourusername/django-etl-framework.git#egg=django-etl-framework

# Your other dependencies
psycopg2-binary>=2.9.0  # PostgreSQL
PyMySQL>=1.0.0          # MySQL
```

Then install with:
```bash
pip install -r requirements.txt
```

### **Development Setup**

For development across multiple projects:

```bash
# Install in editable mode with dev tools
pip install -e /path/to/django_etl_framework[dev,database]

# Install pre-commit hooks (if available)
pre-commit install
```

## ⚙️ **Django Settings Configuration**

Add the ETL framework to your Django project:

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Add the ETL framework
    'django_etl',
    
    # Your other apps
    'your_app',
]

# ETL Framework Configuration
ETL_CONFIG = {
    'DEFAULT_BATCH_SIZE': 1000,
    'ENABLE_VALIDATION': True,
    'ENABLE_PROFILING': True,
    'ENABLE_ROLLBACK': True,
    'LOG_LEVEL': 'INFO',
    'TRANSFORMER_DISCOVERY_PATHS': [
        'your_app.transformers',
        'your_app.etl',
        'your_app.migrations.transformers',
    ],
    'PERFORMANCE_MONITORING': {
        'ENABLED': True,
        'MEMORY_THRESHOLD_MB': 500,
        'TIME_THRESHOLD_SECONDS': 60,
    },
    'VALIDATION_RULES': {
        'HEALTHCARE_MODE': True,  # Enable healthcare-specific validations
        'STRICT_MODE': False,     # Set to True for strict validation
    }
}

# Database Configuration (if using multiple databases)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # or postgresql, sqlite3
        'NAME': 'your_database',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    },
    # Legacy database for ETL source
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'legacy_database',
        'USER': 'legacy_user',
        'PASSWORD': 'legacy_password',
        'HOST': 'legacy_host',
        'PORT': '3306',
    }
}

# Database routing for ETL operations
DATABASE_ROUTERS = ['django_etl.routers.ETLRouter']
```

## 🗃️ **Database Setup**

Run migrations to create the ETL framework tables:

```bash
# Create and apply migrations
python manage.py makemigrations django_etl
python manage.py migrate django_etl

# If you want to use the ETL admin interface
python manage.py migrate
```

## 🔧 **Creating Transformers**

### 1. **Basic Transformer Structure**

Create a `transformers.py` file in your app:

```python
# your_app/transformers.py

from django_etl import BaseTransformer
from django.db import transaction
from .models import YourModel
from legacy_app.models import LegacyModel

class YourModelTransformer(BaseTransformer):
    """
    Transform legacy data to new YourModel format
    """
    
    def __init__(self):
        super().__init__()
        self.batch_size = 500
        self.description = "Migrate legacy data to YourModel"
    
    def get_source_data(self):
        """Get data from legacy database"""
        return LegacyModel.objects.using('legacy').all()
    
    def transform_batch(self, batch):
        """Transform a batch of legacy records"""
        transformed_records = []
        
        for legacy_record in batch:
            try:
                transformed_record = YourModel(
                    name=legacy_record.legacy_name,
                    description=legacy_record.legacy_description,
                    created_at=legacy_record.legacy_created_date,
                    # Add your transformation logic here
                )
                transformed_records.append(transformed_record)
            except Exception as e:
                self.add_error(f"Failed to transform record {legacy_record.id}: {e}")
        
        return transformed_records
    
    def save_batch(self, transformed_batch):
        """Save transformed records to new database"""
        with transaction.atomic():
            YourModel.objects.bulk_create(
                transformed_batch,
                ignore_conflicts=True  # Skip duplicates
            )
            return len(transformed_batch)
```

## 🎯 **Management Commands**

The framework includes enhanced management commands from your original UHMS project:

### 1. **Basic Usage**

```bash
# Run all transformers
python manage.py migrate_legacy_data

# Run specific transformers
python manage.py migrate_legacy_data --only=users,departments

# Dry run (no database changes)
python manage.py migrate_legacy_data --dry-run

# With custom logging
python manage.py migrate_legacy_data --log-file=migration.log --log-level=DEBUG
```

### 2. **Advanced Options**

```bash
# Enable all framework features
python manage.py migrate_legacy_data \
    --enable-rollback \
    --enable-validation \
    --batch-size=500 \
    --log-level=INFO

# Specify transformer paths
python manage.py migrate_legacy_data \
    --transformer-paths="myapp.transformers,otherapp.etl" \
    --log-file=migration.log

# Use the alternative ETL command
python manage.py etl --list  # List available transformers
python manage.py etl --run=users --dry-run
```

## 📊 **Admin Interface**

The framework includes a comprehensive Django admin interface:

### 1. **Accessing the Admin**

```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ETL-specific admin (optional)
    path('etl-admin/', include('django_etl.urls')),
]
```

### 2. **Admin Features**

- **Migration Logs**: View detailed logs of all transformations
- **Performance Metrics**: Monitor memory usage, processing rates
- **Validation Results**: Review validation errors and warnings
- **Session Tracking**: Group related transformations together
- **Export Functionality**: Export migration data for analysis

## 🔍 **Monitoring and Debugging**

### 1. **Built-in Profiling**

```python
# In your transformer
class MyTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.enable_profiling = True  # Enable performance monitoring
        
    def transform_batch(self, batch):
        # Profiling happens automatically
        with self.profiler.operation("custom_operation"):
            # Your custom operation
            result = expensive_operation()
        return result
```

## 🔄 **Rollback and Recovery**

### 1. **Automatic Rollback**

```python
class MyTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.enable_rollback = True  # Enable automatic rollback
        
    def transform(self):
        # If any error occurs, rollback will happen automatically
        return super().transform()
```

## 📈 **Best Practices**

### 1. **Performance Optimization**

```python
class OptimizedTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.batch_size = 1000  # Optimal batch size
        self.enable_profiling = True
        
    def get_source_data(self):
        # Use select_related/prefetch_related for performance
        return LegacyModel.objects.using('legacy').select_related(
            'related_model'
        ).prefetch_related('many_to_many_field')
```

## 🚀 **Deployment Considerations**

### 1. **Production Settings**

```python
# production_settings.py
ETL_CONFIG.update({
    'LOG_LEVEL': 'WARNING',  # Reduce logging in production
    'ENABLE_PROFILING': False,  # Disable profiling overhead
    'DEFAULT_BATCH_SIZE': 5000,  # Larger batches for better performance
})
```

## 📚 **Additional Resources**

- **Framework Documentation**: See README.md for detailed API documentation
- **Healthcare Validation**: Built-in healthcare-specific validation rules
- **Performance Monitoring**: Detailed profiling and performance recommendations
- **Multi-Database Support**: Handle complex database routing scenarios

## 🆘 **Troubleshooting**

### Common Issues

1. **Import Errors**: Ensure django_etl is in INSTALLED_APPS
2. **Database Errors**: Check database routing configuration
3. **Memory Issues**: Reduce batch_size or enable memory monitoring
4. **Performance**: Enable profiling to identify bottlenecks

### Getting Help

- Check the migration logs in Django admin
- Enable DEBUG logging for detailed information
- Use dry-run mode to test transformations safely
