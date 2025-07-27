# migration_core/base.py

import logging
import time
from collections import defaultdict
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from django.db import transaction, connections
from django.core.exceptions import ValidationError

# Import new enhancements
from .profiler import ETLProfiler
from .validators import DataQualityValidator, ValidationSeverity
from .rollback import ETLRollbackManager
from .config import config_manager


class BaseTransformer:
    """
    Base class for all data transformers.
    Provides common functionality for migrating legacy data.
    """

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)
        self.logger = logging.getLogger(f"migration.{self.__class__.__name__}")
        self.start_time = None
        self.legacy_db = "legacy"  # Default legacy database alias
        
        # New enhancements
        self.config = config_manager.get_transformation_config()
        self.profiler = ETLProfiler()
        self.validator = DataQualityValidator()
        self.rollback_manager = ETLRollbackManager()
        self.migration_id = None

    def run(self):
        """
        Override this method with your transformation logic.
        This method should handle the actual data transformation.
        """
        raise NotImplementedError("Subclasses must implement the run() method.")

    def safe_run(self, *, dry_run=False, enable_rollback=True):
        """
        Safely run the transformer with proper error handling and logging.
        """
        self.start_time = time.time()
        self.migration_id = f"{self.__class__.__name__}_{int(self.start_time)}"

        if dry_run:
            self.log_info("Dry run mode: no data will be saved.")

        # Create rollback snapshot if enabled
        snapshot = None
        if enable_rollback and not dry_run:
            try:
                affected_models = getattr(self, 'affected_models', [])
                if affected_models:
                    snapshot = self.rollback_manager.create_snapshot(
                        self.migration_id,
                        self.__class__.__name__,
                        affected_models
                    )
                    self.log_info(f"Created rollback snapshot: {snapshot.migration_id}")
            except Exception as e:
                self.log_warning(f"Could not create rollback snapshot: {e}")

        try:
            with self.profiler.profile_operation("total_migration"):
                if dry_run:
                    # Run without transaction for dry run
                    result = self.run()
                else:
                    with transaction.atomic():
                        result = self.run()

            self._log_completion_stats()
            return result

        except Exception as e:
            self.errors.append(str(e))
            self.logger.error(f"Error during migration: {e}", exc_info=True)
            
            # Attempt automatic rollback if enabled
            if snapshot and enable_rollback:
                try:
                    self.log_info("Attempting automatic rollback...")
                    success = self.rollback_manager.rollback_migration(self.migration_id)
                    if success:
                        self.log_info("Automatic rollback completed successfully")
                    else:
                        self.log_error("Automatic rollback failed")
                except Exception as rollback_error:
                    self.log_error(f"Rollback failed: {rollback_error}")
            
            raise

    def _log_completion_stats(self):
        """Log completion statistics"""
        duration = time.time() - self.start_time if self.start_time else 0

        if self.errors:
            self.log_warning(
                f"Completed with {len(self.errors)} errors: {self.errors[:3]}..."
            )

        if self.warnings:
            self.log_info(f"Completed with {len(self.warnings)} warnings")

        if self.stats:
            stats_msg = ", ".join([f"{k}: {v}" for k, v in self.stats.items()])
            self.log_info(f"Statistics - {stats_msg}")

        self.log_info(f"Transformation completed in {duration:.2f}s")

    # Logging methods
    def log_info(self, message):
        """Log info message (use this instead of print)"""
        self.logger.info(message)

    def log_warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
        self.warnings.append(message)

    def log_error(self, message):
        """Log error message"""
        self.logger.error(message)
        self.errors.append(message)

    # ETL Utility Methods
    def extract_data(self, model_class, filters=None, batch_size=1000):
        """
        Extract data from legacy database with optional filtering and batching

        Args:
            model_class: Django model class to extract from
            filters: Dict of filter conditions
            batch_size: Number of records to fetch at once

        Yields:
            Batches of model instances
        """
        self.log_info(f"Extracting data from {model_class.__name__}")

        queryset = model_class.objects.using(self.legacy_db)

        if filters:
            queryset = queryset.filter(**filters)

        total_count = queryset.count()
        self.log_info(f"Found {total_count} records to process")
        self.stats["total_extracted"] = total_count

        for i in range(0, total_count, batch_size):
            batch = list(queryset[i : i + batch_size])
            self.log_info(
                f"Processing batch {i//batch_size + 1} ({len(batch)} records)"
            )
            yield batch

    def check_duplicates(self, target_model, field_name, value):
        """
        Check if a record already exists in the target database

        Args:
            target_model: Django model class to check against
            field_name: Field name to check
            value: Value to look for

        Returns:
            Existing instance or None
        """
        try:
            return target_model.objects.filter(**{field_name: value}).first()
        except Exception as e:
            self.log_error(f"Error checking duplicates for {field_name}={value}: {e}")
            return None

    def bulk_create_with_logging(self, model_class, instances, batch_size=1000):
        """
        Bulk create instances with progress logging

        Args:
            model_class: Target model class
            instances: List of model instances to create
            batch_size: Number of instances to create per batch

        Returns:
            Number of created instances
        """
        if not instances:
            self.log_info("No instances to create")
            return 0

        total = len(instances)
        created_count = 0

        self.log_info(f"Bulk creating {total} {model_class.__name__} instances")

        for i in range(0, total, batch_size):
            batch = instances[i : i + batch_size]
            try:
                model_class.objects.bulk_create(batch, batch_size=batch_size)
                created_count += len(batch)
                self.log_info(
                    f"Created batch {i//batch_size + 1}: {len(batch)} instances"
                )
            except Exception as e:
                self.log_error(f"Error creating batch {i//batch_size + 1}: {e}")

        self.stats["created"] = created_count
        self.log_info(f"Successfully created {created_count}/{total} instances")
        return created_count

    def validate_data(self, instance, required_fields=None):
        """
        Validate model instance data

        Args:
            instance: Model instance to validate
            required_fields: List of required field names

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Check required fields
        if required_fields:
            for field in required_fields:
                if not hasattr(instance, field) or getattr(instance, field) is None:
                    errors.append(f"Missing required field: {field}")

        # Run model validation
        try:
            instance.full_clean()
        except ValidationError as e:
            errors.extend(
                [f"{field}: {error}" for field, error in e.message_dict.items()]
            )
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        return len(errors) == 0, errors

    def transform_field(self, value, transformations):
        """
        Apply a series of transformations to a field value

        Args:
            value: Original value
            transformations: List of transformation functions

        Returns:
            Transformed value
        """
        result = value
        for transform_func in transformations:
            try:
                result = transform_func(result)
            except Exception as e:
                self.log_warning(f"Transformation failed for value '{value}': {e}")
                break
        return result

    def map_foreign_key(self, legacy_id, mapping_dict, default=None):
        """
        Map legacy foreign key to new foreign key using a mapping dictionary

        Args:
            legacy_id: Legacy foreign key value
            mapping_dict: Dictionary mapping legacy IDs to new IDs
            default: Default value if mapping not found

        Returns:
            Mapped foreign key or default
        """
        if legacy_id in mapping_dict:
            return mapping_dict[legacy_id]

        if default is not None:
            self.log_warning(
                f"No mapping found for legacy ID {legacy_id}, using default: {default}"
            )
            return default

        self.log_error(f"No mapping found for legacy ID {legacy_id}")
        return None

    def execute_raw_sql(self, sql, params=None, database="default"):
        """
        Execute raw SQL query

        Args:
            sql: SQL query string
            params: Query parameters
            database: Database alias to use

        Returns:
            Query results
        """
        try:
            with connections[database].cursor() as cursor:
                cursor.execute(sql, params or [])
                if sql.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                return cursor.rowcount
        except Exception as e:
            self.log_error(f"SQL execution failed: {e}")
            raise

    def create_id_mapping(
        self, legacy_model, target_model, legacy_field="id", target_field="legacy_id"
    ):
        """
        Create a mapping dictionary between legacy and new IDs

        Args:
            legacy_model: Legacy model class
            target_model: Target model class
            legacy_field: Field name in legacy model
            target_field: Field name in target model that stores legacy ID

        Returns:
            Dictionary mapping legacy IDs to new instances
        """
        self.log_info(
            f"Creating ID mapping between {legacy_model.__name__} and {target_model.__name__}"
        )

        mapping = {}

        # Get all target instances that have legacy IDs
        target_instances = target_model.objects.filter(
            **{f"{target_field}__isnull": False}
        )

        for instance in target_instances:
            legacy_id = getattr(instance, target_field)
            mapping[legacy_id] = instance

        self.log_info(f"Created mapping for {len(mapping)} records")
        return mapping

    def get_or_create_with_logging(self, model_class, defaults=None, **lookup):
        """
        Get or create instance with logging

        Args:
            model_class: Model class
            defaults: Default values for creation
            **lookup: Lookup parameters

        Returns:
            Tuple of (instance, created)
        """
        try:
            instance, created = model_class.objects.get_or_create(
                defaults=defaults or {}, **lookup
            )

            action = "created" if created else "found existing"
            self.log_info(f"{action} {model_class.__name__}: {lookup}")

            if created:
                self.stats["created"] += 1
            else:
                self.stats["existing"] += 1

            return instance, created

        except Exception as e:
            self.log_error(
                f"Error getting or creating {model_class.__name__} with {lookup}: {e}"
            )
            raise

    # New enhanced methods
    def validate_batch_with_rules(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of records using configured validation rules
        
        Args:
            records: List of record dictionaries to validate
            
        Returns:
            Validation summary with results
        """
        with self.profiler.profile_operation("batch_validation"):
            return self.validator.validate_batch(records)
    
    def add_validation_rule(self, field: str, rule_func: Callable, severity: ValidationSeverity = ValidationSeverity.ERROR, message: str = ""):
        """
        Add a validation rule to the transformer
        
        Args:
            field: Field name to validate
            rule_func: Function that returns True if valid
            severity: Severity level of validation failure
            message: Custom error message
        """
        self.validator.add_rule(field, rule_func, severity, message)
    
    def batch_process_with_retry(self, data_source, process_func: Callable, batch_size: int = None) -> Dict[str, Any]:
        """
        Process data in batches with retry logic
        
        Args:
            data_source: Iterable data source
            process_func: Function to process each batch
            batch_size: Override default batch size
            
        Returns:
            Processing summary
        """
        batch_size = batch_size or self.config.batch_size
        max_retries = self.config.max_retries
        retry_delay = self.config.retry_delay
        
        results = {
            'total_batches': 0,
            'successful_batches': 0,
            'failed_batches': 0,
            'retried_batches': 0,
            'total_records': 0
        }
        
        batch = []
        for item in data_source:
            batch.append(item)
            
            if len(batch) >= batch_size:
                self._process_batch_with_retry(batch, process_func, max_retries, retry_delay, results)
                batch = []
                results['total_batches'] += 1
        
        # Process remaining items
        if batch:
            self._process_batch_with_retry(batch, process_func, max_retries, retry_delay, results)
            results['total_batches'] += 1
        
        return results
    
    def _process_batch_with_retry(self, batch: List[Any], process_func: Callable, max_retries: int, retry_delay: int, results: Dict[str, Any]):
        """Process a single batch with retry logic"""
        for attempt in range(max_retries + 1):
            try:
                with self.profiler.profile_operation(f"batch_processing_attempt_{attempt}"):
                    process_func(batch)
                results['successful_batches'] += 1
                results['total_records'] += len(batch)
                if attempt > 0:
                    results['retried_batches'] += 1
                break
            except Exception as e:
                if attempt < max_retries:
                    self.log_warning(f"Batch processing failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(retry_delay)
                else:
                    self.log_error(f"Batch processing failed after {max_retries + 1} attempts: {e}")
                    results['failed_batches'] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report"""
        return self.profiler.get_performance_report()
    
    def rollback_migration(self) -> bool:
        """Rollback the current migration"""
        if not self.migration_id:
            self.log_error("No migration ID available for rollback")
            return False
        
        try:
            return self.rollback_manager.rollback_migration(self.migration_id)
        except Exception as e:
            self.log_error(f"Rollback failed: {e}")
            return False
    
    def cleanup_temp_data(self):
        """Clean up temporary data and resources"""
        try:
            # Override in subclasses for specific cleanup
            self.log_info("Performing cleanup...")
        except Exception as e:
            self.log_warning(f"Cleanup warning: {e}")
    
    def get_migration_summary(self) -> Dict[str, Any]:
        """Get comprehensive migration summary"""
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            'migration_id': self.migration_id,
            'transformer_name': self.__class__.__name__,
            'duration_seconds': duration,
            'status': 'completed' if not self.errors else 'failed',
            'statistics': dict(self.stats),
            'errors': self.errors,
            'warnings': self.warnings,
            'performance_report': self.get_performance_report(),
            'timestamp': datetime.now()
        }
