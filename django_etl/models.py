"""
Django ETL Framework Models
Provides migration logging and tracking capabilities
"""

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
import json


class MigrationLog(models.Model):
    """
    Enhanced model to log ETL migration activities with comprehensive tracking.
    Includes performance metrics, validation results, and detailed statistics.
    """

    # Basic migration information
    transformer = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Name of the transformer that was executed",
    )
    run_at = models.DateTimeField(
        default=timezone.now, db_index=True, help_text="When the migration was executed"
    )
    duration_seconds = models.FloatField(help_text="Total execution time in seconds")
    success = models.BooleanField(
        default=True, help_text="Whether the migration completed successfully"
    )
    dry_run = models.BooleanField(
        default=False, help_text="Whether this was a dry run (no actual changes)"
    )
    error_message = models.TextField(
        blank=True, null=True, help_text="Error message if the migration failed"
    )

    # Enhanced tracking fields
    batch_size = models.IntegerField(
        null=True, blank=True, help_text="Batch size used for processing"
    )
    total_records = models.IntegerField(
        null=True, blank=True, help_text="Total number of records processed"
    )

    # JSON fields for detailed information (with fallback for databases without JSON support)
    statistics_json = models.TextField(
        blank=True, null=True, help_text="JSON-encoded statistics about the migration"
    )
    performance_data_json = models.TextField(
        blank=True, null=True, help_text="JSON-encoded performance metrics"
    )
    validation_results_json = models.TextField(
        blank=True, null=True, help_text="JSON-encoded validation results"
    )

    # System information
    system_info_json = models.TextField(
        blank=True,
        null=True,
        help_text="JSON-encoded system information during migration",
    )

    class Meta:
        ordering = ["-run_at"]
        verbose_name = "Migration Log"
        verbose_name_plural = "Migration Logs"
        indexes = [
            models.Index(fields=["transformer", "run_at"]),
            models.Index(fields=["success", "run_at"]),
            models.Index(fields=["dry_run", "run_at"]),
        ]

    def __str__(self):
        status = "✅" if self.success else "❌"
        mode = " (DRY RUN)" if self.dry_run else ""
        return f"[{status}] {self.transformer}{mode} @ {self.run_at.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def statistics(self):
        """Get statistics as a Python dictionary"""
        if self.statistics_json:
            try:
                return json.loads(self.statistics_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @statistics.setter
    def statistics(self, value):
        """Set statistics from a Python dictionary"""
        if value:
            self.statistics_json = json.dumps(value, default=str)
        else:
            self.statistics_json = None

    @property
    def performance_data(self):
        """Get performance data as a Python dictionary"""
        if self.performance_data_json:
            try:
                return json.loads(self.performance_data_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @performance_data.setter
    def performance_data(self, value):
        """Set performance data from a Python dictionary"""
        if value:
            self.performance_data_json = json.dumps(value, default=str)
        else:
            self.performance_data_json = None

    @property
    def validation_results(self):
        """Get validation results as a Python dictionary"""
        if self.validation_results_json:
            try:
                return json.loads(self.validation_results_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @validation_results.setter
    def validation_results(self, value):
        """Set validation results from a Python dictionary"""
        if value:
            self.validation_results_json = json.dumps(value, default=str)
        else:
            self.validation_results_json = None

    @property
    def system_info(self):
        """Get system info as a Python dictionary"""
        if self.system_info_json:
            try:
                return json.loads(self.system_info_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @system_info.setter
    def system_info(self, value):
        """Set system info from a Python dictionary"""
        if value:
            self.system_info_json = json.dumps(value, default=str)
        else:
            self.system_info_json = None

    def get_formatted_duration(self):
        """Get human-readable duration"""
        if self.duration_seconds < 1:
            return f"{self.duration_seconds * 1000:.0f}ms"
        elif self.duration_seconds < 60:
            return f"{self.duration_seconds:.1f}s"
        else:
            minutes = int(self.duration_seconds // 60)
            seconds = self.duration_seconds % 60
            return f"{minutes}m {seconds:.1f}s"

    def get_performance_summary(self):
        """Get a summary of performance metrics"""
        perf_data = self.performance_data
        if not perf_data:
            return "No performance data available"

        summary = []

        # Memory usage
        if "memory" in perf_data:
            memory = perf_data["memory"]
            if "peak_mb" in memory:
                summary.append(f"Peak memory: {memory['peak_mb']:.1f}MB")

        # Processing rate
        if self.total_records and self.duration_seconds:
            rate = self.total_records / self.duration_seconds
            summary.append(f"Rate: {rate:.1f} records/sec")

        # Operation counts
        operations = perf_data.get("operations", {})
        if operations:
            for op, stats in operations.items():
                count = stats.get("count", 0)
                if count > 0:
                    summary.append(f"{op}: {count}")

        return " | ".join(summary)

    def get_validation_summary(self):
        """Get a summary of validation results"""
        validation = self.validation_results
        if not validation:
            return "No validation data available"

        summary = []

        # Error counts by severity
        for severity in ["ERROR", "WARNING", "INFO"]:
            count = validation.get(f"{severity.lower()}_count", 0)
            if count > 0:
                summary.append(f"{severity}s: {count}")

        # Overall status
        if validation.get("passed", True):
            summary.insert(0, "✅ PASSED")
        else:
            summary.insert(0, "❌ FAILED")

        return " | ".join(summary)


class MigrationRunSummary(models.Model):
    """
    Model to track overall migration run sessions.
    Groups multiple transformer executions together.
    """

    session_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique identifier for this migration session",
    )
    started_at = models.DateTimeField(
        default=timezone.now, help_text="When the migration session started"
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="When the migration session completed"
    )
    dry_run = models.BooleanField(
        default=False, help_text="Whether this was a dry run session"
    )
    total_transformers = models.IntegerField(
        default=0, help_text="Total number of transformers in this session"
    )
    successful_transformers = models.IntegerField(
        default=0, help_text="Number of transformers that completed successfully"
    )
    failed_transformers = models.IntegerField(
        default=0, help_text="Number of transformers that failed"
    )
    total_records_processed = models.IntegerField(
        default=0, help_text="Total records processed across all transformers"
    )

    # System context
    user = models.CharField(
        max_length=100, blank=True, help_text="User who initiated the migration"
    )
    command_args = models.TextField(blank=True, help_text="Command line arguments used")

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Migration Run Summary"
        verbose_name_plural = "Migration Run Summaries"

    def __str__(self):
        status = "✅" if self.is_successful else "❌" if self.is_complete else "🔄"
        mode = " (DRY RUN)" if self.dry_run else ""
        return f"[{status}] Session {self.session_id}{mode} - {self.successful_transformers}/{self.total_transformers} successful"

    @property
    def is_complete(self):
        """Check if the migration session is complete"""
        return self.completed_at is not None

    @property
    def is_successful(self):
        """Check if all transformers in the session were successful"""
        return self.is_complete and self.failed_transformers == 0

    @property
    def duration(self):
        """Get the total duration of the migration session"""
        if not self.is_complete:
            return None
        return (self.completed_at - self.started_at).total_seconds()

    def get_formatted_duration(self):
        """Get human-readable duration"""
        duration = self.duration
        if duration is None:
            return "In progress..."

        if duration < 1:
            return f"{duration * 1000:.0f}ms"
        elif duration < 60:
            return f"{duration:.1f}s"
        else:
            minutes = int(duration // 60)
            seconds = duration % 60
            return f"{minutes}m {seconds:.1f}s"

    def get_migration_logs(self):
        """Get all migration logs for this session"""
        # This would need to be implemented based on how session tracking is done
        # For now, return logs from the same time period
        start_time = self.started_at
        end_time = self.completed_at or timezone.now()

        return MigrationLog.objects.filter(
            run_at__gte=start_time, run_at__lte=end_time, dry_run=self.dry_run
        )
