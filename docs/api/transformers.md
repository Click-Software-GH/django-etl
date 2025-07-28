# Transformers API

The transformer system is the core of the Django ETL framework. You create custom transformers by inheriting from `BaseTransformer` and implementing your data migration logic.

## Creating Your First Transformer

### Basic Transformer Structure

```python
# myapp/transformers/patients.py
from django_etl.base import BaseTransformer
from django.contrib.auth.models import User
from myapp.models import Patient
from legacy.models import LegacyPatient


class PatientTransformer(BaseTransformer):
    """Migrate patient data from legacy system to new system"""

    # Define which models this transformer affects (for rollback)
    affected_models = [Patient, User]
    
    def run(self):
        """Your transformation logic goes here"""

        self.log_info("Starting patient migration...")
        
        # Extract data from legacy database
        for batch in self.extract_data(LegacyPatient, batch_size=500):
            self.process_patient_batch(batch)
        
        self.log_info("Patient migration completed!")
    
    def process_patient_batch(self, legacy_patients):
        """Process a batch of legacy patients"""

        new_patients = []
        
        for legacy_patient in legacy_patients:
            # Transform legacy data to new format
            patient = Patient(
                first_name=legacy_patient.fname,
                last_name=legacy_patient.lname,
                date_of_birth=legacy_patient.birth_date,
                # ... other field mappings
            )
            
            # Validate the data
            is_valid, errors = self.validate_data(patient, required_fields=['first_name', 'last_name'])
            if not is_valid:
                self.log_warning(f"Invalid patient data: {errors}")
                continue
            
            new_patients.append(patient)
        
        # Bulk create the new patients
        self.bulk_create_with_logging(Patient, new_patients)
```

### Running Your Transformer

```python
# Run in Django shell or management command
python manage.py shell

>>> from myapp.transformers.patients import PatientTransformer
>>> transformer = PatientTransformer()
>>> transformer.safe_run()
```

## BaseTransformer API Reference

### Core Methods You Override

#### `run()`

**Purpose:** Contains your main transformation logic  
**Required:** Yes - you must implement this method  
**Usage:** This is where you write your ETL pipeline

```python
def run(self):
    """Your transformation logic"""
    # 1. Extract data from source
    # 2. Transform the data
    # 3. Load into target system
    pass
```

### Execution Methods

#### `safe_run(dry_run=False, enable_rollback=True)`

**Purpose:** Safely execute your transformer with error handling  
**Returns:** Result from your `run()` method  

**Parameters:**
- `dry_run` (bool): If True, runs without saving data (for testing)
- `enable_rollback` (bool): If True, creates rollback snapshots

```python
# Normal execution
result = transformer.safe_run()

# Test without saving data
result = transformer.safe_run(dry_run=True)

# Run without rollback capability
result = transformer.safe_run(enable_rollback=False)
```

**What happens during execution:**
1. Creates rollback snapshot (if enabled)
2. Starts performance profiling
3. Executes your `run()` method in a database transaction
4. Logs completion statistics
5. Automatically rolls back on errors (if enabled)

### Data Extraction Methods

#### `extract_data(model_class, filters=None, batch_size=1000)`

**Purpose:** Extract data from legacy database in batches  
**Returns:** Generator yielding batches of model instances

```python
# Extract all patients
for batch in self.extract_data(LegacyPatient):
    self.process_batch(batch)

# Extract with filters
for batch in self.extract_data(LegacyPatient, 
                              filters={'status': 'active'},
                              batch_size=2000):
    self.process_batch(batch)

# Extract with date range
from datetime import date
filters = {
    'created_date__gte': date(2020, 1, 1),
    'created_date__lt': date(2023, 1, 1)
}
for batch in self.extract_data(LegacyPatient, filters=filters):
    self.process_batch(batch)
```

### Data Loading Methods

#### `bulk_create_with_logging(model_class, instances, batch_size=1000)`

**Purpose:** Efficiently create many model instances with progress logging  
**Returns:** Number of successfully created instances

```python
# Create patients in batches
new_patients = [Patient(...), Patient(...), ...]
created_count = self.bulk_create_with_logging(Patient, new_patients)
```

#### `get_or_create_with_logging(model_class, defaults=None, **lookup)`

**Purpose:** Get existing instance or create new one with logging  
**Returns:** Tuple of (instance, created_boolean)

```python
# Get or create a department
department, created = self.get_or_create_with_logging(
    Department,
    defaults={'name': 'Cardiology', 'budget': 100000},
    code='CARD'
)

if created:
    self.log_info(f"Created new department: {department}")
else:
    self.log_info(f"Using existing department: {department}")
```

### Data Validation Methods

#### `validate_data(instance, required_fields=None)`

**Purpose:** Validate a model instance before saving  
**Returns:** Tuple of (is_valid_boolean, error_list)

```python
patient = Patient(first_name="John", last_name="Doe")

is_valid, errors = self.validate_data(
    patient, 
    required_fields=['first_name', 'last_name', 'date_of_birth']
)

if is_valid:
    patient.save()
else:
    self.log_warning(f"Validation failed: {errors}")
```

#### `add_validation_rule(field, rule_func, severity=ERROR, message="")`

**Purpose:** Add custom validation rules to your transformer

```python
from django_etl.validators import ValidationSeverity

# Add custom validation rule
def validate_age(date_of_birth):
    """Patients must be under 120 years old"""

    from datetime import date
    age = (date.today() - date_of_birth).days / 365.25
    return age < 120

self.add_validation_rule(
    'date_of_birth',
    validate_age,
    severity=ValidationSeverity.ERROR,
    message="Patient age cannot exceed 120 years"
)
```

#### `validate_batch_with_rules(records)`

**Purpose:** Validate a batch of records using your custom rules  
**Returns:** Validation summary dictionary

```python
records = [
    {'first_name': 'John', 'date_of_birth': date(1950, 1, 1)},
    {'first_name': 'Jane', 'date_of_birth': date(1800, 1, 1)},  # Invalid age
]

validation_result = self.validate_batch_with_rules(records)
print(f"Valid records: {validation_result['valid_count']}")
print(f"Invalid records: {validation_result['invalid_count']}")
```

### Data Transformation Methods

#### `transform_field(value, transformations)`

**Purpose:** Apply multiple transformations to a field value  
**Returns:** Transformed value

```python
# Define transformation functions
def uppercase(value):
    return value.upper() if value else value

def strip_whitespace(value):
    return value.strip() if value else value

def standardize_phone(value):
    if value:
        # Remove all non-digits
        return ''.join(filter(str.isdigit, value))
    return value

# Apply transformations
transformations = [strip_whitespace, uppercase]
clean_name = self.transform_field(legacy_patient.name, transformations)

phone_transformations = [strip_whitespace, standardize_phone]
clean_phone = self.transform_field(legacy_patient.phone, phone_transformations)
```

#### `map_foreign_key(legacy_id, mapping_dict, default=None)`

**Purpose:** Map legacy foreign keys to new system foreign keys  
**Returns:** Mapped ID or default value

```python
# First, create a mapping of legacy IDs to new instances
department_mapping = self.create_id_mapping(
    LegacyDepartment,     # Legacy model
    Department,           # Target model
    legacy_field='id',    # Field in legacy model
    target_field='legacy_id'  # Field in target model that stores legacy ID
)

# Then use the mapping
legacy_dept_id = legacy_patient.department_id
new_department = self.map_foreign_key(
    legacy_dept_id, 
    department_mapping, 
    default=None
)

if new_department:
    patient.department = new_department
else:
    self.log_warning(f"No department mapping for ID {legacy_dept_id}")
```

#### `create_id_mapping(legacy_model, target_model, legacy_field="id", target_field="legacy_id")`

**Purpose:** Create a mapping dictionary between legacy and new record IDs  
**Returns:** Dictionary mapping legacy IDs to new model instances

```python
# Create mapping for departments
department_mapping = self.create_id_mapping(
    LegacyDepartment,     # Source model
    Department,           # Target model
    legacy_field='id',    # Primary key field in legacy model
    target_field='legacy_dept_id'  # Field in target model storing legacy ID
)

# Now you can quickly map legacy department IDs to new Department instances
new_dept = department_mapping.get(legacy_dept_id)
```

### Utility Methods

#### `check_duplicates(target_model, field_name, value)`

**Purpose:** Check if a record already exists to avoid duplicates  
**Returns:** Existing instance or None

```python
# Check if patient already exists by social security number
existing_patient = self.check_duplicates(Patient, 'ssn', legacy_patient.ssn)

if existing_patient:
    self.log_info(f"Patient {legacy_patient.ssn} already exists, skipping")
    continue
else:
    # Create new patient
    new_patient = Patient(ssn=legacy_patient.ssn, ...)
```

#### `execute_raw_sql(sql, params=None, database="default")`

**Purpose:** Execute raw SQL queries when Django ORM isn't sufficient  
**Returns:** Query results (for SELECT) or affected row count

```python
# Complex data extraction
sql = """
SELECT p.*, d.name as dept_name 
FROM legacy_patients p 
JOIN legacy_departments d ON p.dept_id = d.id 
WHERE p.status = %s AND p.created_date > %s
"""

results = self.execute_raw_sql(
    sql, 
    params=['active', '2020-01-01'],
    database='legacy'
)

for row in results:
    # Process raw SQL results
    patient_data = {
        'name': row[1],
        'department_name': row[-1]
    }
```

### Batch Processing with Retry

#### `batch_process_with_retry(data_source, process_func, batch_size=None)`

**Purpose:** Process large datasets in batches with automatic retry on failures  
**Returns:** Processing summary dictionary

```python
def process_patient_batch(batch):
    """Process a batch of patient records"""

    patients = []
    for record in batch:
        patient = Patient(
            first_name=record["first_name"],
            last_name=record["last_name"],
        )
        patients.append(patient)
    
    Patient.objects.bulk_create(patients)

# Process data with retry logic
data_source = LegacyPatient.objects.using('legacy').all()
summary = self.batch_process_with_retry(
    data_source, 
    process_patient_batch,
    batch_size=1000
)

print(f"Processed {summary['total_batches']} batches")
print(f"Successful: {summary['successful_batches']}")
print(f"Failed: {summary['failed_batches']}")
print(f"Retried: {summary['retried_batches']}")
```

### Logging Methods

#### `log_info(message)`, `log_warning(message)`, `log_error(message)`

**Purpose:** Log messages with appropriate severity levels

```python
def run(self):
    self.log_info("Starting patient migration")
    
    try:
        # Your transformation logic
        self.log_info("Processing 1000 patients...")
        
    except ValidationError as e:
        self.log_warning(f"Data validation issue: {e}")
        
    except Exception as e:
        self.log_error(f"Critical error: {e}")
        raise
```

### Performance and Monitoring

#### `get_performance_report()`

**Purpose:** Get detailed performance metrics for your transformation  
**Returns:** Performance report dictionary

```python
def run(self):
    # Your transformation logic here
    pass

# After running the transformer
transformer = PatientTransformer()
transformer.safe_run()

report = transformer.get_performance_report()
print(f"Total execution time: {report['total_time']}")
print(f"Database operations: {report['database_operations']}")
print(f"Memory usage: {report['memory_usage']}")
```

#### `get_migration_summary()`

**Purpose:** Get comprehensive summary of the migration  
**Returns:** Migration summary dictionary

```python
summary = transformer.get_migration_summary()
print(f"Migration ID: {summary['migration_id']}")
print(f"Status: {summary['status']}")
print(f"Duration: {summary['duration_seconds']} seconds")
print(f"Records processed: {summary['statistics']}")
print(f"Errors: {len(summary['errors'])}")
print(f"Warnings: {len(summary['warnings'])}")
```

### Rollback Methods

#### `rollback_migration()`

**Purpose:** Manually rollback the current migration  
**Returns:** Boolean indicating success

```python
# Run a migration
transformer = PatientTransformer()
transformer.safe_run()

# Later, if you need to rollback
success = transformer.rollback_migration()
if success:
    print("Migration rolled back successfully")
else:
    print("Rollback failed")
```

## Configuration Properties

Your transformer automatically has access to configuration settings:

```python
class MyTransformer(BaseTransformer):
    def run(self):
        # Access configuration settings
        batch_size = self.config.batch_size
        max_retries = self.config.max_retries
        validation_enabled = self.config.enable_validation
        
        self.log_info(f"Using batch size: {batch_size}")
```

## Error Handling

The framework provides automatic error handling, but you can add custom logic:

```python
class RobustTransformer(BaseTransformer):
    def run(self):
        for batch in self.extract_data(LegacyData):
            try:
                self.process_batch(batch)
            except ValidationError as e:
                self.log_warning(f"Validation error in batch: {e}")
                # Continue with next batch
                continue
            except DatabaseError as e:
                self.log_error(f"Database error: {e}")
                # This will trigger automatic rollback
                raise
```

## Complete Example: Patient Migration

Here's a complete example showing all the concepts together:

```python
from django_etl.base import BaseTransformer
from django_etl.validators import ValidationSeverity
from datetime import date, timedelta
from myapp.models import Patient, Department
from legacy.models import LegacyPatient, LegacyDepartment

class ComprehensivePatientTransformer(BaseTransformer):
    """Complete patient migration with all features"""
    
    affected_models = [Patient, Department]
    
    def __init__(self):
        super().__init__()
        self.department_mapping = {}
        self.setup_validation_rules()
    
    def setup_validation_rules(self):
        """Set up custom validation rules"""
        def validate_age(birth_date):
            if not birth_date:
                return False
            age = (date.today() - birth_date).days / 365.25
            return 0 <= age <= 120
        
        def validate_phone(phone):
            if not phone:
                return True  # Optional field
            return len(phone.replace('-', '').replace(' ', '')) >= 10
        
        self.add_validation_rule('date_of_birth', validate_age, 
                               ValidationSeverity.ERROR, 
                               "Patient age must be between 0 and 120 years")
        
        self.add_validation_rule('phone', validate_phone,
                               ValidationSeverity.WARNING,
                               "Phone number should have at least 10 digits")
    
    def run(self):
        """Main transformation logic"""
        self.log_info("Starting comprehensive patient migration")
        
        # Step 1: Migrate departments first
        self.migrate_departments()
        
        # Step 2: Create department mapping
        self.create_department_mapping()
        
        # Step 3: Migrate patients
        self.migrate_patients()
        
        self.log_info("Patient migration completed successfully")
    
    def migrate_departments(self):
        """Migrate departments first"""
        self.log_info("Migrating departments...")
        
        departments = []
        for legacy_dept in LegacyDepartment.objects.using('legacy').all():
            # Check for duplicates
            existing = self.check_duplicates(Department, 'name', legacy_dept.name)
            if existing:
                continue
            
            dept = Department(
                name=legacy_dept.name,
                budget=legacy_dept.budget or 0,
                legacy_dept_id=legacy_dept.id
            )
            departments.append(dept)
        
        created = self.bulk_create_with_logging(Department, departments)
        self.log_info(f"Created {created} departments")
    
    def create_department_mapping(self):
        """Create mapping between legacy and new department IDs"""
        self.department_mapping = self.create_id_mapping(
            LegacyDepartment,
            Department,
            legacy_field='id',
            target_field='legacy_dept_id'
        )
    
    def migrate_patients(self):
        """Migrate patient data with full validation"""
        self.log_info("Starting patient migration...")
        
        # Define transformations
        name_transformations = [
            lambda x: x.strip() if x else x,
            lambda x: x.title() if x else x
        ]
        
        phone_transformations = [
            lambda x: x.strip() if x else x,
            lambda x: ''.join(filter(str.isdigit, x)) if x else x,
            lambda x: f"{x[:3]}-{x[3:6]}-{x[6:]}" if x and len(x) == 10 else x
        ]
        
        # Process in batches
        def process_patient_batch(batch):
            new_patients = []
            
            for legacy_patient in batch:
                # Check for duplicates
                existing = self.check_duplicates(Patient, 'ssn', legacy_patient.ssn)
                if existing:
                    self.log_info(f"Patient {legacy_patient.ssn} already exists")
                    continue
                
                # Transform data
                patient = Patient(
                    first_name=self.transform_field(legacy_patient.fname, name_transformations),
                    last_name=self.transform_field(legacy_patient.lname, name_transformations),
                    date_of_birth=legacy_patient.birth_date,
                    phone=self.transform_field(legacy_patient.phone, phone_transformations),
                    ssn=legacy_patient.ssn,
                    legacy_patient_id=legacy_patient.id
                )
                
                # Map department
                if legacy_patient.dept_id:
                    department = self.map_foreign_key(
                        legacy_patient.dept_id,
                        self.department_mapping
                    )
                    patient.department = department
                
                # Validate data
                is_valid, errors = self.validate_data(
                    patient,
                    required_fields=['first_name', 'last_name', 'ssn']
                )
                
                if not is_valid:
                    self.log_warning(f"Invalid patient {legacy_patient.ssn}: {errors}")
                    continue
                
                new_patients.append(patient)
            
            # Bulk create
            if new_patients:
                self.bulk_create_with_logging(Patient, new_patients)
        
        # Process all patients with retry logic
        data_source = LegacyPatient.objects.using('legacy').all()
        summary = self.batch_process_with_retry(
            data_source,
            process_patient_batch,
            batch_size=500
        )
        
        self.log_info(f"Migration summary: {summary}")

# Usage
if __name__ == "__main__":
    transformer = ComprehensivePatientTransformer()
    
    # Test run first
    transformer.safe_run(dry_run=True)
    
    # If test passes, run for real
    result = transformer.safe_run()
    
    # Get detailed report
    summary = transformer.get_migration_summary()
    performance = transformer.get_performance_report()
    
    print("Migration completed!")
    print(f"Status: {summary['status']}")
    print(f"Duration: {summary['duration_seconds']:.2f} seconds")
    print(f"Records processed: {summary['statistics']['total_extracted']}")
    print(f"Records created: {summary['statistics']['created']}")
```

This example shows how to use all the major features of the BaseTransformer class to create a robust, production-ready data migration.
