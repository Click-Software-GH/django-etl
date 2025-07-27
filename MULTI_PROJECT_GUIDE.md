# Using Django ETL Framework Across Multiple Projects

## 🚀 Installation Methods

### Method 1: Install from PyPI (Recommended for Production)

```bash
# Install the package
pip install django-etl-framework

# Or with specific database support
pip install django-etl-framework[mysql,postgresql]
```

### Method 2: Install from Source (for Development)

```bash
# Clone or copy the django_etl_framework directory to your projects

# Install in development mode
pip install -e /path/to/django_etl_framework

# Or create a wheel and install
cd /path/to/django_etl_framework
python setup.py bdist_wheel
pip install dist/django_etl_framework-1.0.0-py3-none-any.whl
```

### Method 3: Local Package (Quick Setup)

```bash
# Copy the django_etl directory to your Django project
cp -r django_etl_framework/django_etl /path/to/your/project/
```

## 📁 Project Integration Examples

### Project 1: Healthcare Management System (UHMS)

```python
# settings/base.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other apps
    'django_etl',  # Add the ETL framework
    'patients',
    'appointments',
    'billing',
]

# ETL Configuration
ETL_FRAMEWORK = {
    'BATCH_SIZE': 2000,  # Large batches for UHMS
    'ENABLE_VALIDATION': True,
    'VALIDATION_MODE': 'strict',
    'BACKUP_DIRECTORY': '/var/backups/uhms/etl',
    'DEFAULT_LEGACY_DB': 'legacy_uhms',
}

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uhms_production',
        # ... connection details
    },
    'legacy_uhms': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'old_uhms_system',
        # ... connection details
    }
}
```

```python
# patients/transformers.py
from django_etl import BaseTransformer, HealthcareValidationRules, ValidationSeverity
from .models import Patient
from legacy.models import LegacyPatient

class UHMSPatientTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.affected_models = [Patient]
        self.setup_validation_rules()
    
    def setup_validation_rules(self):
        self.add_validation_rule(
            'patient_id', 
            HealthcareValidationRules.patient_id_format,
            ValidationSeverity.ERROR
        )
        self.add_validation_rule(
            'age',
            HealthcareValidationRules.age_range,
            ValidationSeverity.ERROR
        )
    
    def run(self):
        for batch in self.extract_data(LegacyPatient, batch_size=2000):
            # UHMS-specific transformation logic
            processed = []
            for legacy_patient in batch:
                patient = Patient(
                    patient_id=legacy_patient.id,
                    name=legacy_patient.full_name.title(),
                    age=legacy_patient.age,
                    # ... UHMS-specific fields
                )
                processed.append(patient)
            
            self.bulk_create_with_logging(Patient, processed)
```

### Project 2: E-commerce Platform

```python
# settings/production.py
INSTALLED_APPS = [
    # ... e-commerce apps
    'django_etl',  # Same ETL framework, different config
    'products',
    'orders',
    'customers',
]

# ETL Configuration for E-commerce
ETL_FRAMEWORK = {
    'BATCH_SIZE': 5000,  # Larger batches for product data
    'ENABLE_VALIDATION': True,
    'VALIDATION_MODE': 'lenient',  # More forgiving for product data
    'BACKUP_DIRECTORY': '/var/backups/ecommerce/etl',
    'DEFAULT_LEGACY_DB': 'legacy_shop',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecommerce_db',
    },
    'legacy_shop': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'old_shop_system',
    }
}
```

```python
# products/transformers.py
from django_etl import BaseTransformer, CommonValidationRules, ValidationSeverity
from .models import Product
from legacy.models import LegacyProduct

class ProductTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.affected_models = [Product]
        self.setup_validation_rules()
    
    def setup_validation_rules(self):
        self.add_validation_rule(
            'name', 
            CommonValidationRules.not_empty_string,
            ValidationSeverity.ERROR
        )
        self.add_validation_rule(
            'price',
            CommonValidationRules.numeric_range(min_val=0),
            ValidationSeverity.ERROR
        )
    
    def run(self):
        for batch in self.extract_data(LegacyProduct, batch_size=5000):
            # E-commerce specific transformation
            processed = []
            for legacy_product in batch:
                product = Product(
                    name=legacy_product.product_name,
                    price=legacy_product.cost,
                    # ... e-commerce specific fields
                )
                processed.append(product)
            
            self.bulk_create_with_logging(Product, processed)
```

### Project 3: Financial Services

```python
# settings.py
INSTALLED_APPS = [
    # ... financial apps
    'django_etl',
    'accounts',
    'transactions',
    'compliance',
]

# High-security ETL configuration
ETL_FRAMEWORK = {
    'BATCH_SIZE': 500,  # Smaller batches for financial data
    'ENABLE_VALIDATION': True,
    'VALIDATION_MODE': 'strict',
    'ENABLE_ROLLBACK': True,  # Critical for financial data
    'BACKUP_DIRECTORY': '/secure/backups/financial/etl',
    'DEFAULT_LEGACY_DB': 'legacy_banking',
}
```

```python
# accounts/transformers.py
from django_etl import BaseTransformer, CommonValidationRules, ValidationSeverity
from decimal import Decimal

class AccountTransformer(BaseTransformer):
    def setup_validation_rules(self):
        # Financial-specific validation
        self.add_validation_rule(
            'account_number',
            lambda x: len(str(x)) >= 10,
            ValidationSeverity.ERROR,
            "Account number must be at least 10 digits"
        )
        
        self.add_validation_rule(
            'balance',
            lambda x: isinstance(x, (int, float, Decimal)),
            ValidationSeverity.ERROR,
            "Balance must be numeric"
        )
```

## 🔧 Management Commands Usage

Each project can use the same management commands:

```bash
# UHMS Project
cd /path/to/uhms
python manage.py etl analyze --table patients --database legacy_uhms

# E-commerce Project  
cd /path/to/ecommerce
python manage.py etl analyze --table products --database legacy_shop

# Financial Project
cd /path/to/financial
python manage.py etl analyze --table accounts --database legacy_banking
```

## 🎯 Best Practices for Multiple Projects

### 1. **Consistent Package Structure**
```
your_project/
├── requirements/
│   ├── base.txt (include django-etl-framework)
│   └── production.txt
├── settings/
│   ├── base.py (ETL framework config)
│   └── production.py
└── apps/
    └── your_app/
        ├── models.py
        ├── transformers.py (your ETL logic)
        └── management/commands/migrate_data.py
```

### 2. **Environment-Specific Configuration**

```python
# settings/base.py
ETL_FRAMEWORK = {
    'BATCH_SIZE': int(os.getenv('ETL_BATCH_SIZE', 1000)),
    'ENABLE_VALIDATION': os.getenv('ETL_VALIDATION', 'true').lower() == 'true',
    'BACKUP_DIRECTORY': os.getenv('ETL_BACKUP_DIR', '/tmp/etl_backups'),
}

# .env file per project
ETL_BATCH_SIZE=2000
ETL_VALIDATION=true
ETL_BACKUP_DIR=/var/backups/project/etl
```

### 3. **Custom Management Commands**

```python
# your_app/management/commands/migrate_legacy_data.py
from django.core.management.base import BaseCommand
from your_app.transformers import YourTransformer

class Command(BaseCommand):
    help = 'Migrate legacy data for this specific project'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--table', type=str)
    
    def handle(self, *args, **options):
        transformer = YourTransformer()
        
        result = transformer.safe_run(
            dry_run=options['dry_run'],
            enable_rollback=not options['dry_run']
        )
        
        summary = transformer.get_migration_summary()
        self.stdout.write(
            self.style.SUCCESS(
                f"Migration completed: {summary['statistics']}"
            )
        )
```

### 4. **Shared Validation Rules**

```python
# Create a shared validation module
# common/validators.py
from django_etl import CommonValidationRules

class CompanyValidationRules(CommonValidationRules):
    @staticmethod
    def company_id_format(value):
        """Company-specific ID validation"""
        return value and len(str(value)) == 8 and str(value).isdigit()
    
    @staticmethod
    def department_code(value):
        """Validate department codes"""
        valid_codes = ['HR', 'IT', 'FIN', 'OPS', 'MKT']
        return str(value).upper() in valid_codes

# Use in any project transformer
from common.validators import CompanyValidationRules

class EmployeeTransformer(BaseTransformer):
    def setup_validation_rules(self):
        self.add_validation_rule(
            'employee_id',
            CompanyValidationRules.company_id_format
        )
```

## 📦 Package Distribution

### Internal PyPI Server (Enterprise)
```bash
# Set up internal PyPI server
pip install twine

# Build and upload to internal server
python setup.py sdist bdist_wheel
twine upload --repository-url http://internal-pypi.company.com dist/*

# Install from internal server in projects
pip install --index-url http://internal-pypi.company.com django-etl-framework
```

### Git Submodules (Version Control)
```bash
# Add as submodule in each project
git submodule add https://github.com/company/django-etl-framework.git libs/django_etl

# Install from submodule
pip install -e libs/django_etl

# Update across projects
git submodule update --remote
```

## 🚀 The Result

With this setup, you can:

1. **✅ Share the same ETL framework** across all Django projects
2. **✅ Customize configuration** per project needs  
3. **✅ Maintain consistent patterns** across different domains
4. **✅ Update framework centrally** and deploy to all projects
5. **✅ Use project-specific transformers** with shared validation rules
6. **✅ Leverage same management commands** everywhere

**Your ETL framework is now ready for enterprise-wide deployment! 🎯**
