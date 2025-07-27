# Rollback & Recovery API

The Django ETL framework includes a comprehensive rollback system that provides data protection and recovery capabilities for your transformations.

## Overview

The rollback system provides:

- **Automatic snapshots** before transformations
- **Data backup and restore** capabilities  
- **Migration tracking** with detailed metadata
- **Selective rollback** for specific transformations
- **Recovery verification** to ensure data integrity

## How Rollback Works

### Automatic Protection

When you run a transformer with `enable_rollback=True` (the default), the system automatically:

1. **Creates a snapshot** with current data state
2. **Records metadata** about the transformation  
3. **Tracks affected models** and record counts
4. **Enables automatic rollback** if the transformation fails
5. **Stores recovery information** for manual rollbacks

```python
# Rollback is enabled by default
transformer = PatientTransformer()
transformer.safe_run()  # Automatic rollback protection

# Explicitly enable/disable rollback
transformer.safe_run(enable_rollback=True)   # Protected run
transformer.safe_run(enable_rollback=False)  # Faster, unprotected run
```

### Manual Rollback

You can manually rollback transformations using the rollback API:

```python
# Run a transformation
transformer = PatientTransformer()
result = transformer.safe_run()

# Later, if you need to rollback
success = transformer.rollback_migration()
if success:
    print("Migration rolled back successfully")
else:
    print("Rollback failed - check logs for details")
```

## Rollback API Reference

### Transformer Rollback Methods

#### `rollback_migration()`

**Purpose:** Rollback the current migration  
**Returns:** Boolean indicating success/failure

```python
class PatientTransformer(BaseTransformer):
    affected_models = [Patient, MedicalRecord]  # Required for rollback
    
    def run(self):
        # Your transformation logic
        self.migrate_patients()
    
    def rollback_if_needed(self):
        """Example of conditional rollback"""
        # Check if rollback is needed based on business logic
        patient_count = Patient.objects.count()
        if patient_count == 0:  # Something went wrong
            self.log_warning("No patients found after migration, rolling back...")
            success = self.rollback_migration()
            if not success:
                self.log_error("Rollback failed!")
                raise Exception("Migration failed and rollback unsuccessful")

# Usage
transformer = PatientTransformer()
transformer.safe_run()

# Manual rollback
if transformer.rollback_migration():
    print("Successfully rolled back migration")
```

### Rollback Manager API

For advanced rollback operations, you can use the rollback manager directly:

```python
from django_etl.rollback import ETLRollbackManager

# Create rollback manager
rollback_manager = ETLRollbackManager()

# List available snapshots
snapshots = rollback_manager.list_snapshots()
for snapshot in snapshots:
    print(f"Migration: {snapshot.migration_id}")
    print(f"Transformer: {snapshot.transformer_name}")
    print(f"Date: {snapshot.timestamp}")
    print(f"Tables: {', '.join(snapshot.affected_tables)}")

# Rollback specific migration
success = rollback_manager.rollback_migration("PatientTransformer_1640995200")
```

#### `list_snapshots()`

**Purpose:** Get list of available rollback snapshots  
**Returns:** List of MigrationSnapshot objects

```python
rollback_manager = ETLRollbackManager()
snapshots = rollback_manager.list_snapshots()

print(f"Found {len(snapshots)} available snapshots:")
for snapshot in snapshots:
    print(f"  {snapshot.migration_id} - {snapshot.transformer_name} ({snapshot.timestamp})")
```

#### `rollback_migration(migration_id)`

**Purpose:** Rollback a specific migration by ID  
**Returns:** Boolean indicating success

```python
# Rollback specific migration
migration_id = "PatientTransformer_1640995200" 
success = rollback_manager.rollback_migration(migration_id)

if success:
    print(f"Successfully rolled back {migration_id}")
else:
    print(f"Failed to rollback {migration_id}")
```

#### `create_snapshot(migration_id, transformer_name, affected_models)`

**Purpose:** Manually create a rollback snapshot  
**Returns:** MigrationSnapshot object

```python
from myapp.models import Patient, Department

# Manual snapshot creation
snapshot = rollback_manager.create_snapshot(
    migration_id="manual_backup_001",
    transformer_name="ManualBackup", 
    affected_models=[Patient, Department]
)

print(f"Created snapshot: {snapshot.migration_id}")
print(f"Backup location: {snapshot.backup_location}")
```

## Configuring Rollback Behavior

### Model Declaration

To enable rollback for your transformers, declare which models are affected:

```python
class PatientTransformer(BaseTransformer):
    # Required: List all models this transformer modifies
    affected_models = [
        Patient,           # Primary model
        MedicalRecord,     # Related model
        Insurance,         # Another related model
        User,             # If you create user accounts
    ]
    
    def run(self):
        # Your transformation logic
        pass
```

### Rollback Configuration

Configure rollback behavior in your ETL settings:

```python
# settings.py
ETL_CONFIG = {
    'ROLLBACK': {
        'BACKUP_DIRECTORY': '/opt/etl/backups',     # Where to store backups
        'ENABLE_AUTO_ROLLBACK': True,              # Auto-rollback on failure
        'KEEP_SNAPSHOTS_DAYS': 30,                 # How long to keep snapshots
        'COMPRESSION_ENABLED': True,               # Compress backup files
        'VERIFY_ROLLBACK': True,                   # Verify rollback success
    },
    
    # Feature flags
    'ENABLE_ROLLBACK': True,                       # Global rollback enable/disable
}
```

## Rollback Scenarios

### Automatic Rollback on Failure

The most common use case is automatic rollback when transformations fail:

```python
class RobustPatientTransformer(BaseTransformer):
    affected_models = [Patient, MedicalRecord]
    
    def run(self):
        try:
            # Risky transformation
            self.migrate_complex_data()
            
        except DatabaseError as e:
            self.log_error(f"Database error: {e}")
            # Automatic rollback will be triggered
            raise
        
        except ValidationError as e:
            self.log_error(f"Validation failed: {e}")
            # Automatic rollback will be triggered
            raise

# Usage - rollback happens automatically on exception
transformer = RobustPatientTransformer()
try:
    transformer.safe_run(enable_rollback=True)
    print("Migration completed successfully")
except Exception as e:
    print(f"Migration failed: {e}")
    print("Automatic rollback was attempted")
```

### Conditional Rollback

Rollback based on business logic validation:

```python
class BusinessValidatedTransformer(BaseTransformer):
    affected_models = [Patient]
    
    def run(self):
        # Run the transformation
        self.migrate_patients()
        
        # Validate business rules after migration
        if not self.validate_business_rules():
            self.log_error("Business validation failed")
            # Trigger manual rollback
            if self.rollback_migration():
                self.log_info("Successfully rolled back due to business rule violation")
            else:
                self.log_error("Rollback failed - manual intervention required")
                raise Exception("Migration and rollback both failed")
    
    def validate_business_rules(self):
        """Validate business rules after transformation"""
        # Example: Ensure no patients lost during migration
        legacy_count = LegacyPatient.objects.using('legacy').count()
        new_count = Patient.objects.count()
        
        if new_count < legacy_count * 0.95:  # Allow 5% tolerance
            self.log_error(f"Patient count mismatch: {new_count} vs {legacy_count}")
            return False
        
        # Example: Ensure data integrity
        patients_without_names = Patient.objects.filter(
            first_name__isnull=True
        ).count()
        
        if patients_without_names > 0:
            self.log_error(f"Found {patients_without_names} patients without names")
            return False
        
        return True
```

### Partial Rollback

Rollback only specific parts of a complex transformation:

```python
class ComplexTransformer(BaseTransformer):
    affected_models = [Patient, Department, Insurance]
    
    def run(self):
        # Step 1: Migrate departments
        dept_snapshot = self.create_checkpoint("departments")
        self.migrate_departments()
        
        # Step 2: Migrate patients  
        patient_snapshot = self.create_checkpoint("patients")
        try:
            self.migrate_patients()
        except Exception as e:
            self.log_error(f"Patient migration failed: {e}")
            # Rollback only patients, keep departments
            self.rollback_to_checkpoint(patient_snapshot)
            raise
        
        # Step 3: Migrate insurance
        try:
            self.migrate_insurance()
        except Exception as e:
            self.log_error(f"Insurance migration failed: {e}")
            # Rollback patients and insurance, keep departments
            self.rollback_to_checkpoint(dept_snapshot)
            raise
    
    def create_checkpoint(self, name):
        """Create a named checkpoint for partial rollback"""
        checkpoint_id = f"{self.migration_id}_{name}"
        return self.rollback_manager.create_snapshot(
            checkpoint_id,
            f"{self.__class__.__name__}_{name}",
            self.affected_models
        )
    
    def rollback_to_checkpoint(self, snapshot):
        """Rollback to a specific checkpoint"""
        success = self.rollback_manager.rollback_migration(snapshot.migration_id)
        if success:
            self.log_info(f"Rolled back to checkpoint: {snapshot.migration_id}")
        else:
            self.log_error(f"Failed to rollback checkpoint: {snapshot.migration_id}")
        return success
```

## Advanced Rollback Features

### Rollback Verification

Verify that rollback was successful:

```python
class VerifiedTransformer(BaseTransformer):
    affected_models = [Patient]
    
    def run(self):
        # Store pre-migration state
        original_count = Patient.objects.count()
        original_sample = list(Patient.objects.values('id', 'first_name')[:10])
        
        try:
            # Run risky transformation
            self.risky_transformation()
            
        except Exception as e:
            self.log_error(f"Transformation failed: {e}")
            
            # Automatic rollback will occur
            # Let's verify it worked
            if self.verify_rollback_success(original_count, original_sample):
                self.log_info("Rollback verification successful")
            else:
                self.log_error("Rollback verification failed!")
                raise Exception("Rollback did not restore original state")
            
            raise  # Re-raise original exception
    
    def verify_rollback_success(self, expected_count, expected_sample):
        """Verify rollback restored the original state"""
        # Check count
        current_count = Patient.objects.count()
        if current_count != expected_count:
            self.log_error(f"Count mismatch: {current_count} vs {expected_count}")
            return False
        
        # Check sample data
        current_sample = list(Patient.objects.values('id', 'first_name')[:10])
        if current_sample != expected_sample:
            self.log_error("Sample data doesn't match original")
            return False
        
        return True
```

### Cross-Database Rollback

Handle rollback across multiple databases:

```python
class CrossDatabaseTransformer(BaseTransformer):
    affected_models = [Patient, ExternalRecord]  # Models in different databases
    
    def run(self):
        try:
            # Modify default database
            self.migrate_patients()
            
            # Modify external database  
            self.migrate_external_records()
            
        except Exception as e:
            self.log_error(f"Cross-database migration failed: {e}")
            # Custom rollback for multiple databases
            self.rollback_all_databases()
            raise
    
    def rollback_all_databases(self):
        """Custom rollback for multiple databases"""
        success = True
        
        # Rollback main database
        if not self.rollback_migration():
            self.log_error("Failed to rollback main database")
            success = False
        
        # Rollback external database
        if not self.rollback_external_database():
            self.log_error("Failed to rollback external database")
            success = False
        
        return success
    
    def rollback_external_database(self):
        """Custom rollback logic for external database"""
        try:
            # Implement external database rollback
            # This might involve API calls, file operations, etc.
            return True
        except Exception as e:
            self.log_error(f"External database rollback failed: {e}")
            return False
```

## Management Command Integration

### List Available Rollbacks

```bash
# Custom management command to list rollbacks
python manage.py etl_rollback --list

# Output:
# Available rollback snapshots:
#   PatientTransformer_1640995200 - 2024-01-01 10:00:00 (patients, medical_records)
#   DepartmentTransformer_1640991600 - 2024-01-01 09:00:00 (departments)
```

### Execute Rollback via Command Line

```bash
# Rollback specific migration
python manage.py etl_rollback --migration-id PatientTransformer_1640995200

# Rollback with verification
python manage.py etl_rollback --migration-id PatientTransformer_1640995200 --verify

# List and rollback interactively
python manage.py etl_rollback --interactive
```

## Monitoring and Alerts

### Rollback Notifications

```python
class MonitoredTransformer(BaseTransformer):
    def safe_run(self, **kwargs):
        try:
            return super().safe_run(**kwargs)
        except Exception as e:
            # Send alert about failed migration and rollback
            self.send_rollback_alert(str(e))
            raise
    
    def send_rollback_alert(self, error_message):
        """Send notification about rollback event"""
        alert_data = {
            'transformer': self.__class__.__name__,
            'migration_id': self.migration_id,
            'error': error_message,
            'timestamp': datetime.now().isoformat(),
            'rollback_attempted': True
        }
        
        # Send to monitoring system
        try:
            import requests
            requests.post(
                'https://monitoring.company.com/alerts/etl-rollback',
                json=alert_data,
                timeout=5
            )
        except Exception as alert_error:
            self.log_warning(f"Could not send rollback alert: {alert_error}")
```

## Best Practices

### 1. Always Declare Affected Models

```python
# Good: Explicitly declare all affected models
class PatientTransformer(BaseTransformer):
    affected_models = [Patient, MedicalRecord, Insurance, User]

# Bad: Missing affected models means incomplete rollback
class IncompleteTransformer(BaseTransformer):
    # Missing affected_models declaration
    pass
```

### 2. Test Rollback in Development

```python
# Test rollback functionality
def test_rollback():
    transformer = PatientTransformer()
    
    # Record initial state
    initial_count = Patient.objects.count()
    
    # Run and immediately rollback
    transformer.safe_run()
    transformer.rollback_migration()
    
    # Verify rollback worked
    final_count = Patient.objects.count()
    assert final_count == initial_count, "Rollback didn't restore original state"
```

### 3. Monitor Rollback Performance

```python
class PerformanceMonitoredTransformer(BaseTransformer):
    def rollback_migration(self):
        start_time = time.time()
        success = super().rollback_migration()
        rollback_duration = time.time() - start_time
        
        self.log_info(f"Rollback completed in {rollback_duration:.2f}s")
        
        # Alert if rollback is slow
        if rollback_duration > 300:  # 5 minutes
            self.log_warning(f"Slow rollback detected: {rollback_duration:.2f}s")
        
        return success
```

### 4. Clean Up Old Snapshots

```python
# Regular cleanup of old snapshots
from django.core.management.base import BaseCommand
from django_etl.rollback import ETLRollbackManager

class Command(BaseCommand):
    def handle(self, *args, **options):
        manager = ETLRollbackManager()
        deleted_count = manager.cleanup_old_snapshots(days=30)
        self.stdout.write(f"Deleted {deleted_count} old snapshots")
```

The rollback system provides comprehensive data protection for your ETL operations, ensuring you can always recover from failures or unwanted changes.
