# Quick Start

Get your first ETL transformation running in 5 minutes!

## Prerequisites

Make sure you have:

- [x] Django ETL Framework installed
- [x] Framework added to `INSTALLED_APPS`
- [x] Migrations run (`python manage.py migrate django_etl`)

!!! tip "Need help with installation?"
    Check our [Installation Guide](installation.md) if you haven't set up the framework yet.

## Step 1: Configure Your Databases

Add your source and target databases to Django's `DATABASES` setting:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'my_new_system',
        'HOST': 'localhost',
        'PORT': 5432,
        'USER': 'postgres',
        'PASSWORD': 'password',
    },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'old_system',
        'HOST': 'localhost',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'password',
    }
}

# Basic ETL configuration
ETL_CONFIG = {
    'PROJECT_NAME': 'My First ETL',
    'REQUIRED_DATABASES': ['default', 'legacy'],
}
```

## Step 2: Create Your Models

Define models for your source and target data:

=== "Target Model (New System)"

    ```python
    # myapp/models.py
    from django.db import models
    
    class Customer(models.Model):
        first_name = models.CharField(max_length=100)
        last_name = models.CharField(max_length=100)
        email = models.EmailField(unique=True)
        phone = models.CharField(max_length=20, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
        
        def __str__(self):
            return f"{self.first_name} {self.last_name}"
    ```

=== "Source Model (Legacy System)"

    ```python
    # legacy/models.py
    from django.db import models
    
    class LegacyCustomer(models.Model):
        customer_name = models.CharField(max_length=200)
        email_address = models.CharField(max_length=100)
        phone_number = models.CharField(max_length=50)
        registration_date = models.DateTimeField()
        
        class Meta:
            managed = False  # Don't let Django manage this table
            db_table = 'customers'  # Existing table name
    ```

## Step 3: Create Your First Transformer

Create a transformer to migrate data from legacy to new system:

```python
# myapp/transformers/customer_transformer.py
from django_etl import BaseTransformer
from myapp.models import Customer
from legacy.models import LegacyCustomer

class CustomerTransformer(BaseTransformer):
    """Transform legacy customers to new customer model"""
    
    def __init__(self):
        super().__init__()
        self.batch_size = 500
        self.description = "Migrate customer data from legacy system"
    
    def get_source_data(self):
        """Get customers from legacy database"""
        return LegacyCustomer.objects.using('legacy').all()
    
    def transform_batch(self, batch):
        """Transform a batch of legacy customers"""
        customers = []
        
        for legacy_customer in batch:
            try:
                # Split name into first and last
                name_parts = legacy_customer.customer_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                customer_data = {
                    'first_name': self.clean_name(first_name),
                    'last_name': self.clean_name(last_name),
                    'email': self.clean_email(legacy_customer.email_address),
                    'phone': self.clean_phone(legacy_customer.phone_number),
                }
                
                # Validate the data
                if self.validate_customer_data(customer_data):
                    customers.append(Customer(**customer_data))
                    
            except Exception as e:
                self.add_error(f"Failed to transform customer {legacy_customer.id}: {e}")
        
        return customers
    
    def save_batch(self, transformed_batch):
        """Save customers to new database"""
        Customer.objects.bulk_create(
            transformed_batch, 
            ignore_conflicts=True,
            update_conflicts=True,
            update_fields=['first_name', 'last_name', 'phone'],
            unique_fields=['email']
        )
        return len(transformed_batch)
    
    # Helper methods
    def clean_name(self, name):
        """Clean and standardize names"""
        return name.strip().title() if name else ""
    
    def clean_email(self, email):
        """Clean email addresses"""
        return email.lower().strip() if email else ""
    
    def clean_phone(self, phone):
        """Clean phone numbers"""
        if not phone:
            return ""
        # Remove non-digits and format
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return digits
    
    def validate_customer_data(self, data):
        """Validate customer data"""
        if not data.get('first_name'):
            self.add_warning("Customer missing first name")
            return False
        
        if not data.get('email'):
            self.add_warning("Customer missing email")
            return False
            
        return True
```

## Step 4: Configure Transformer Discovery

Tell the framework where to find your transformers:

```python
# settings.py
ETL_CONFIG = {
    'PROJECT_NAME': 'My First ETL',
    'TRANSFORMER_DISCOVERY_PATHS': [
        'myapp.transformers',  # Add your transformer module
    ],
    'REQUIRED_DATABASES': ['default', 'legacy'],
}
```

## Step 5: Test Your Transformer

Before running the actual migration, test it with a dry run:

```bash
# Test without making changes
python manage.py migrate_legacy_data --dry-run

# Test specific transformer
python manage.py migrate_legacy_data --only customer --dry-run

# Enable detailed logging
python manage.py migrate_legacy_data --dry-run --log-level DEBUG
```

You should see output like:

```
🚀 Django ETL Framework - Starting Migration
📋 Project: My First ETL
🔍 Environment: development
📊 Discovered 1 transformer(s)

🔄 CustomerTransformer: Migrate customer data from legacy system
  📥 Source: 1,247 records found
  🔧 Processing in batches of 500
  ✅ Batch 1/3: 500 records processed
  ✅ Batch 2/3: 500 records processed  
  ✅ Batch 3/3: 247 records processed
  📊 Total: 1,247 records transformed (DRY RUN - No data saved)

✅ Migration completed successfully!
⏱️  Total time: 2.3 seconds
📈 Performance: 541 records/second
```

## Step 6: Run the Migration

When you're ready, run the actual migration:

```bash
# Run the migration
python manage.py migrate_legacy_data

# Run with specific options
python manage.py migrate_legacy_data \
    --enable-rollback \
    --enable-validation \
    --log-file migration.log
```

## Step 7: Monitor Progress

The framework provides real-time progress updates:

```
🚀 Django ETL Framework - Starting Migration
📋 Project: My First ETL

🔄 CustomerTransformer: Processing...
  📥 Source: 1,247 records
  🔧 Batch 1/3: ████████████████████████████████ 500/500 (100%)
  ✅ Saved 500 records to database
  
  🔧 Batch 2/3: ████████████████████████████████ 500/500 (100%)
  ✅ Saved 500 records to database
  
  🔧 Batch 3/3: ██████████████████████████████ 247/247 (100%)
  ✅ Saved 247 records to database

✅ Migration completed successfully!
📊 Summary:
   • Total records: 1,247
   • Successful: 1,245
   • Warnings: 2
   • Errors: 0
⏱️ Total time: 3.1 seconds
```

## Common Patterns

### Handle Relationships

```python
def transform_batch(self, batch):
    customers = []
    for legacy_customer in batch:
        # Handle foreign key relationships
        try:
            department = Department.objects.get(
                name=legacy_customer.dept_name
            )
        except Department.DoesNotExist:
            department = None
            self.add_warning(f"Department not found: {legacy_customer.dept_name}")
        
        customer = Customer(
            name=legacy_customer.customer_name,
            department=department,
        )
        customers.append(customer)
    
    return customers
```

### Conditional Transformations

```python
def transform_batch(self, batch):
    customers = []
    for legacy_customer in batch:
        # Skip inactive customers
        if legacy_customer.status == 'INACTIVE':
            self.add_info(f"Skipping inactive customer: {legacy_customer.id}")
            continue
        
        # Different logic based on customer type
        if legacy_customer.customer_type == 'PREMIUM':
            priority = Customer.PRIORITY_HIGH
        elif legacy_customer.customer_type == 'STANDARD':
            priority = Customer.PRIORITY_NORMAL
        else:
            priority = Customer.PRIORITY_LOW
        
        customer = Customer(
            name=legacy_customer.customer_name,
            priority=priority,
        )
        customers.append(customer)
    
    return customers
```

### Data Validation

```python
def validate_customer_data(self, data):
    """Comprehensive data validation"""
    errors = []
    
    # Required fields
    if not data.get('first_name'):
        errors.append("Missing first name")
    
    if not data.get('email'):
        errors.append("Missing email")
    elif '@' not in data['email']:
        errors.append("Invalid email format")
    
    # Data format validation
    if data.get('phone') and len(data['phone']) < 10:
        errors.append("Phone number too short")
    
    if errors:
        self.add_error(f"Validation failed: {', '.join(errors)}")
        return False
    
    return True
```

## Next Steps

Congratulations! You've successfully created and run your first ETL transformation. Here's what to explore next:

- **[Creating Transformers](../user-guide/transformers.md)** - Learn advanced transformer patterns
- **[Validation System](../user-guide/validation.md)** - Implement comprehensive data validation
- **[Performance Monitoring](../user-guide/monitoring.md)** - Monitor and optimize your transformations
- **[Error Handling](../user-guide/error-handling.md)** - Handle errors and edge cases
- **[Management Commands](../user-guide/commands.md)** - Explore all available commands

!!! success "Ready for Production?"
    
    Before deploying to production:
    
    1. Test with a subset of your data
    2. Set up proper logging and monitoring
    3. Configure rollback procedures
    4. Review performance benchmarks
    5. Set up alerts for failures
