# Data Validation API

The Django ETL framework includes a comprehensive data validation system that helps ensure data quality during transformations.

## Overview

The validation system provides:

- **Custom validation rules** for any field or data combination
- **Multiple severity levels** (Error, Warning, Info)
- **Batch validation** for processing large datasets efficiently
- **Built-in common validators** for typical data validation scenarios
- **Detailed validation reports** with actionable insights

## Basic Usage

### Adding Validation Rules to Transformers

The easiest way to use validation is through your transformer classes:

```python
from django_etl.base import BaseTransformer
from django_etl.validators import ValidationSeverity
from datetime import date

class PatientTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.setup_validation_rules()
    
    def setup_validation_rules(self):
        """Define validation rules for patient data"""
        
        # Age validation
        def validate_age(birth_date):
            if not birth_date:
                return False
            age = (date.today() - birth_date).days / 365.25
            return 0 <= age <= 120
        
        self.add_validation_rule(
            field='date_of_birth',
            rule_func=validate_age,
            severity=ValidationSeverity.ERROR,
            message="Patient age must be between 0 and 120 years"
        )
        
        # Email validation
        def validate_email(email):
            if not email:
                return True  # Optional field
            return '@' in email and '.' in email.split('@')[1]
        
        self.add_validation_rule(
            field='email',
            rule_func=validate_email,
            severity=ValidationSeverity.WARNING,
            message="Email address format appears invalid"
        )
        
        # SSN validation
        def validate_ssn(ssn):
            if not ssn:
                return False
            # Remove hyphens and check if it's 9 digits
            clean_ssn = ssn.replace('-', '')
            return len(clean_ssn) == 9 and clean_ssn.isdigit()
        
        self.add_validation_rule(
            field='ssn',
            rule_func=validate_ssn,
            severity=ValidationSeverity.ERROR,
            message="SSN must be 9 digits (format: XXX-XX-XXXX)"
        )
    
    def run(self):
        # Your transformation logic
        for batch in self.extract_data(LegacyPatient):
            # Validate batch before processing
            records = [{'date_of_birth': p.birth_date, 'email': p.email, 'ssn': p.ssn} 
                      for p in batch]
            
            validation_result = self.validate_batch_with_rules(records)
            
            if validation_result['error_count'] > 0:
                self.log_warning(f"Found {validation_result['error_count']} validation errors")
                # Handle errors according to your business logic
            
            # Process valid records
            self.process_batch(batch)
```

### Standalone Validation

You can also use the validation system independently:

```python
from django_etl.validators import DataQualityValidator, ValidationSeverity

# Create validator instance
validator = DataQualityValidator()

# Add validation rules
def validate_phone_number(phone):
    if not phone:
        return True  # Optional
    clean_phone = ''.join(filter(str.isdigit, phone))
    return len(clean_phone) >= 10

validator.add_rule(
    field='phone',
    rule_func=validate_phone_number,
    severity=ValidationSeverity.WARNING,
    message="Phone number should have at least 10 digits"
)

# Validate individual records
record = {'phone': '555-123-4567', 'name': 'John Doe'}
results = validator.validate_record(record)

for result in results:
    if not result.is_valid:
        print(f"{result.severity.value}: {result.message}")

# Validate batches
records = [
    {'phone': '555-123-4567', 'name': 'John Doe'},
    {'phone': '123', 'name': 'Jane Smith'},  # Invalid phone
    {'phone': '', 'name': 'Bob Johnson'},    # Empty phone (optional)
]

batch_result = validator.validate_batch(records)
print(f"Valid: {batch_result['valid_count']}, Invalid: {batch_result['invalid_count']}")
```

## Validation Rule API

### `add_validation_rule(field, rule_func, severity, message)`

Add a custom validation rule to your transformer or validator.

**Parameters:**
- `field` (str): Field name to validate
- `rule_func` (callable): Function that returns True if valid, False if invalid
- `severity` (ValidationSeverity): Error level - ERROR, WARNING, or INFO
- `message` (str): Custom error message for validation failures

**Example:**
```python
def validate_positive_number(value):
    return value is not None and value > 0

transformer.add_validation_rule(
    field='salary',
    rule_func=validate_positive_number,
    severity=ValidationSeverity.ERROR,
    message="Salary must be a positive number"
)
```

### `validate_batch_with_rules(records)`

Validate a batch of records using your defined rules.

**Parameters:**
- `records` (List[Dict]): List of record dictionaries to validate

**Returns:**
Dictionary with validation summary:
```python
{
    'total_records': 100,
    'valid_count': 85,
    'invalid_count': 15,
    'error_count': 10,      # ERROR severity violations
    'warning_count': 5,     # WARNING severity violations
    'info_count': 0,        # INFO severity violations
    'results': [            # Detailed validation results
        ValidationResult(...),
        ValidationResult(...),
    ]
}
```

## Built-in Validation Functions

The framework provides common validation functions you can use:

### Date and Time Validation

```python
from django_etl.validators import DateValidator

# Age validation
def setup_date_rules(self):
    # Birth date must be in the past
    self.add_validation_rule(
        'birth_date',
        lambda d: d < date.today() if d else False,
        ValidationSeverity.ERROR,
        "Birth date must be in the past"
    )
    
    # Date must be within reasonable range
    def validate_date_range(birth_date):
        if not birth_date:
            return False
        min_date = date(1900, 1, 1)
        max_date = date.today()
        return min_date <= birth_date <= max_date
    
    self.add_validation_rule(
        'birth_date',
        validate_date_range,
        ValidationSeverity.ERROR,
        "Birth date must be between 1900 and today"
    )
```

### String Validation

```python
def setup_string_rules(self):
    # Required field validation
    def validate_required(value):
        return value is not None and str(value).strip() != ''
    
    self.add_validation_rule(
        'first_name',
        validate_required,
        ValidationSeverity.ERROR,
        "First name is required"
    )
    
    # String length validation
    def validate_length(value, min_len=2, max_len=50):
        if not value:
            return False
        return min_len <= len(str(value).strip()) <= max_len
    
    self.add_validation_rule(
        'first_name',
        lambda v: validate_length(v, 2, 50),
        ValidationSeverity.ERROR,
        "First name must be between 2 and 50 characters"
    )
    
    # Format validation
    def validate_name_format(name):
        if not name:
            return False
        # Only letters, spaces, hyphens, apostrophes
        return re.match(r"^[A-Za-z\s\-']+$", name.strip()) is not None
    
    self.add_validation_rule(
        'first_name',
        validate_name_format,
        ValidationSeverity.WARNING,
        "Name contains unusual characters"
    )
```

### Numeric Validation

```python
def setup_numeric_rules(self):
    # Range validation
    def validate_age_range(age):
        return age is not None and 0 <= age <= 120
    
    self.add_validation_rule(
        'age',
        validate_age_range,
        ValidationSeverity.ERROR,
        "Age must be between 0 and 120"
    )
    
    # Positive number validation
    def validate_positive(value):
        return value is not None and value > 0
    
    self.add_validation_rule(
        'salary',
        validate_positive,
        ValidationSeverity.ERROR,
        "Salary must be positive"
    )
    
    # Decimal precision validation
    def validate_currency(amount):
        if amount is None:
            return False
        # Check for reasonable decimal places (max 2)
        return abs(amount - round(amount, 2)) < 0.001
    
    self.add_validation_rule(
        'salary',
        validate_currency,
        ValidationSeverity.WARNING,
        "Currency amount has too many decimal places"
    )
```

### Email and Contact Validation

```python
import re

def setup_contact_rules(self):
    # Email validation
    def validate_email(email):
        if not email:
            return True  # Optional field
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email.strip()) is not None
    
    self.add_validation_rule(
        'email',
        validate_email,
        ValidationSeverity.WARNING,
        "Email format is invalid"
    )
    
    # Phone validation
    def validate_phone(phone):
        if not phone:
            return True  # Optional field
        # Extract digits only
        digits = ''.join(filter(str.isdigit, phone))
        # US phone number should have 10 digits
        return len(digits) == 10
    
    self.add_validation_rule(
        'phone',
        validate_phone,
        ValidationSeverity.WARNING,
        "Phone number should be 10 digits"
    )
```

## Advanced Validation Patterns

### Cross-Field Validation

Validate relationships between multiple fields:

```python
def setup_cross_field_validation(self):
    # Validate that end date is after start date
    def validate_date_sequence(record):
        start_date = record.get('start_date')
        end_date = record.get('end_date')
        
        if not start_date or not end_date:
            return True  # Skip if either is missing
        
        return start_date <= end_date
    
    # For cross-field validation, validate the entire record
    def validate_record_dates(record_dict):
        return validate_date_sequence(record_dict)
    
    # Add as a record-level validation
    self.validator.add_rule(
        field='date_range',  # Logical field name
        rule_func=validate_record_dates,
        severity=ValidationSeverity.ERROR,
        message="End date must be after start date"
    )
```

### Conditional Validation

Apply validation rules based on conditions:

```python
def setup_conditional_validation(self):
    # Required field only if another field has a value
    def validate_conditional_required(record):
        has_spouse = record.get('marital_status') == 'married'
        spouse_name = record.get('spouse_name')
        
        if has_spouse and not spouse_name:
            return False  # Spouse name required if married
        return True
    
    self.validator.add_rule(
        field='spouse_name',
        rule_func=validate_conditional_required,
        severity=ValidationSeverity.ERROR,
        message="Spouse name is required when marital status is 'married'"
    )
```

### Business Rule Validation

Implement complex business logic:

```python
def setup_business_rules(self):
    # Healthcare-specific: Patient must be 18+ for certain procedures
    def validate_procedure_age(record):
        age = record.get('age')
        procedure_code = record.get('procedure_code')
        
        restricted_procedures = ['SURG001', 'SURG002', 'ANES001']
        
        if procedure_code in restricted_procedures:
            return age is not None and age >= 18
        return True
    
    self.validator.add_rule(
        field='procedure_eligibility',
        rule_func=validate_procedure_age,
        severity=ValidationSeverity.ERROR,
        message="Patient must be 18 or older for this procedure"
    )
    
    # Insurance validation
    def validate_insurance_coverage(record):
        procedure = record.get('procedure_code')
        insurance_type = record.get('insurance_type')
        
        # Business logic: certain procedures not covered by certain insurance
        if insurance_type == 'basic' and procedure in ['COSM001', 'COSM002']:
            return False
        return True
    
    self.validator.add_rule(
        field='insurance_coverage',
        rule_func=validate_insurance_coverage,
        severity=ValidationSeverity.WARNING,
        message="Procedure may not be covered by basic insurance"
    )
```

## Validation Reports and Analysis

### Processing Validation Results

```python
def analyze_validation_results(self, validation_result):
    """Analyze and act on validation results"""
    
    # Log summary
    self.log_info(f"Validation complete: {validation_result['valid_count']} valid, {validation_result['invalid_count']} invalid")
    
    # Handle different severity levels
    if validation_result['error_count'] > 0:
        self.log_error(f"Found {validation_result['error_count']} critical validation errors")
        
        # Option 1: Stop processing on errors
        if self.config.validation_mode == 'strict':
            raise ValueError("Validation errors found in strict mode")
        
        # Option 2: Log errors but continue
        elif self.config.validation_mode == 'lenient':
            self.log_warning("Continuing despite validation errors")
    
    # Process warnings
    if validation_result['warning_count'] > 0:
        self.log_warning(f"Found {validation_result['warning_count']} validation warnings")
        
        # Group warnings by type
        warning_groups = {}
        for result in validation_result['results']:
            if result.severity == ValidationSeverity.WARNING:
                warning_groups.setdefault(result.rule_name, []).append(result)
        
        for rule_name, warnings in warning_groups.items():
            self.log_warning(f"Rule '{rule_name}': {len(warnings)} warnings")
    
    return validation_result['error_count'] == 0  # Return whether validation passed
```

### Exporting Validation Reports

```python
def export_validation_report(self, validation_result, filename):
    """Export detailed validation report"""
    import json
    from datetime import datetime
    
    report = {
        'validation_timestamp': datetime.now().isoformat(),
        'transformer': self.__class__.__name__,
        'summary': {
            'total_records': validation_result['total_records'],
            'valid_count': validation_result['valid_count'],
            'invalid_count': validation_result['invalid_count'],
            'error_count': validation_result['error_count'],
            'warning_count': validation_result['warning_count'],
        },
        'details': []
    }
    
    # Add details for invalid records
    for result in validation_result['results']:
        if not result.is_valid:
            report['details'].append({
                'field': result.field,
                'value': str(result.value),
                'severity': result.severity.value,
                'message': result.message,
                'rule': result.rule_name
            })
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    self.log_info(f"Validation report exported to {filename}")
```

## Performance Considerations

### Batch Size Optimization

```python
def optimize_validation_performance(self):
    """Tips for optimizing validation performance"""
    
    # 1. Process in smaller batches for memory efficiency
    optimal_batch_size = min(self.config.batch_size, 1000)
    
    # 2. Use efficient validation functions
    def fast_email_check(email):
        # Simple check is faster than complex regex for large datasets
        return email and '@' in email and '.' in email
    
    # 3. Skip expensive validations in dry runs
    if not self.dry_run:
        self.add_validation_rule('email', fast_email_check, ValidationSeverity.WARNING)
    
    # 4. Cache validation results for repeated values
    validation_cache = {}
    
    def cached_validation(value):
        if value in validation_cache:
            return validation_cache[value]
        
        result = expensive_validation_function(value)
        validation_cache[value] = result
        return result
```

## Integration with Django Models

### Model-Based Validation

```python
from django.core.exceptions import ValidationError

def setup_model_validation(self):
    """Use Django model validation alongside custom rules"""
    
    def validate_with_model(record):
        """Validate using Django model's built-in validation"""
        try:
            # Create model instance (don't save)
            instance = Patient(
                first_name=record.get('first_name'),
                last_name=record.get('last_name'),
                email=record.get('email')
            )
            
            # Run Django model validation
            instance.full_clean()
            return True
            
        except ValidationError:
            return False
    
    self.validator.add_rule(
        field='model_validation',
        rule_func=validate_with_model,
        severity=ValidationSeverity.ERROR,
        message="Record fails Django model validation"
    )
```

The validation system provides comprehensive data quality assurance for your ETL operations, helping ensure that only clean, valid data enters your target systems.
