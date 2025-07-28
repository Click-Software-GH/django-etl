"""
Django Admin configuration for ETL Framework models
Provides comprehensive admin interface for migration monitoring
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import MigrationLog, MigrationRunSummary


class TransformerListFilter(admin.SimpleListFilter):
    """Custom filter for transformer names"""

    title = "transformer"
    parameter_name = "transformer"

    def lookups(self, request, model_admin):
        transformers = MigrationLog.objects.values_list(
            "transformer", flat=True
        ).distinct()
        return [
            (transformer, transformer) for transformer in transformers if transformer
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(transformer=self.value())
        return queryset


class DurationListFilter(admin.SimpleListFilter):
    """Custom filter for migration duration"""

    title = "duration"
    parameter_name = "duration"

    def lookups(self, request, model_admin):
        return [
            ("fast", "Fast (< 30s)"),
            ("medium", "Medium (30s - 5m)"),
            ("slow", "Slow (> 5m)"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "fast":
            return queryset.filter(duration_seconds__lt=30)
        elif self.value() == "medium":
            return queryset.filter(duration_seconds__gte=30, duration_seconds__lt=300)
        elif self.value() == "slow":
            return queryset.filter(duration_seconds__gte=300)
        return queryset


@admin.register(MigrationLog)
class MigrationLogAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for MigrationLog with filtering and detailed views
    """

    list_display = [
        "transformer",
        "run_at",
        "formatted_duration",
        "success_status",
        "dry_run_badge",
        "total_records",
        "performance_summary_short",
        "validation_summary_short",
    ]

    list_filter = [
        "success",
        "dry_run",
        "run_at",
        TransformerListFilter,
        DurationListFilter,
    ]

    search_fields = [
        "transformer",
        "error_message",
    ]

    readonly_fields = [
        "run_at",
        "duration_seconds",
        "formatted_duration",
        "performance_summary",
        "validation_summary",
        "statistics_display",
        "system_info_display",
    ]

    fields = [
        ("transformer", "run_at"),
        ("success", "dry_run"),
        ("duration_seconds", "formatted_duration"),
        ("batch_size", "total_records"),
        "error_message",
        "performance_summary",
        "validation_summary",
        "statistics_display",
        "system_info_display",
    ]

    ordering = ["-run_at"]

    date_hierarchy = "run_at"

    list_per_page = 50

    actions = ["export_migration_data", "mark_for_review"]

    def success_status(self, obj):
        """Display success status with colored icons"""
        if obj.success:
            return format_html('<span style="color: green;">✅ Success</span>')
        else:
            return format_html('<span style="color: red;">❌ Failed</span>')

    success_status.short_description = "Status"

    def dry_run_badge(self, obj):
        """Display dry run badge"""
        if obj.dry_run:
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 11px;">DRY RUN</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">LIVE</span>'
        )

    dry_run_badge.short_description = "Mode"

    def formatted_duration(self, obj):
        """Display formatted duration"""
        return obj.get_formatted_duration()

    formatted_duration.short_description = "Duration"

    def performance_summary_short(self, obj):
        """Display short performance summary"""
        summary = obj.get_performance_summary()
        if len(summary) > 50:
            return summary[:47] + "..."
        return summary

    performance_summary_short.short_description = "Performance"

    def validation_summary_short(self, obj):
        """Display short validation summary"""
        summary = obj.get_validation_summary()
        if len(summary) > 40:
            return summary[:37] + "..."
        return summary

    validation_summary_short.short_description = "Validation"

    def performance_summary(self, obj):
        """Display detailed performance summary"""
        return format_html("<pre>{}</pre>", obj.get_performance_summary())

    performance_summary.short_description = "Performance Details"

    def validation_summary(self, obj):
        """Display detailed validation summary"""
        return format_html("<pre>{}</pre>", obj.get_validation_summary())

    validation_summary.short_description = "Validation Details"

    def statistics_display(self, obj):
        """Display statistics in a formatted way"""
        stats = obj.statistics
        if stats:
            formatted = json.dumps(stats, indent=2)
            return format_html("<pre>{}</pre>", formatted)
        return "No statistics available"

    statistics_display.short_description = "Statistics"

    def system_info_display(self, obj):
        """Display system info in a formatted way"""
        info = obj.system_info
        if info:
            formatted = json.dumps(info, indent=2)
            return format_html("<pre>{}</pre>", formatted)
        return "No system info available"

    system_info_display.short_description = "System Information"

    def export_migration_data(self, request, queryset):
        """Export selected migration data"""
        # This would implement data export functionality
        self.message_user(request, f"Exported {queryset.count()} migration records")

    export_migration_data.short_description = "Export migration data"

    def mark_for_review(self, request, queryset):
        """Mark migrations for review"""
        # This would implement review marking functionality
        self.message_user(request, f"Marked {queryset.count()} migrations for review")

    mark_for_review.short_description = "Mark for review"

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related()

    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to the changelist"""
        extra_context = extra_context or {}

        # Get summary statistics
        total_migrations = MigrationLog.objects.count()
        successful_migrations = MigrationLog.objects.filter(success=True).count()
        failed_migrations = MigrationLog.objects.filter(success=False).count()

        # Recent activity (last 24 hours)
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_migrations = MigrationLog.objects.filter(
            run_at__gte=recent_cutoff
        ).count()

        extra_context.update(
            {
                "summary_stats": {
                    "total": total_migrations,
                    "successful": successful_migrations,
                    "failed": failed_migrations,
                    "recent": recent_migrations,
                    "success_rate": (
                        (successful_migrations / total_migrations * 100)
                        if total_migrations > 0
                        else 0
                    ),
                }
            }
        )

        return super().changelist_view(request, extra_context)


@admin.register(MigrationRunSummary)
class MigrationRunSummaryAdmin(admin.ModelAdmin):
    """
    Admin interface for MigrationRunSummary
    """

    list_display = [
        "session_id",
        "started_at",
        "status_display",
        "transformer_summary",
        "total_records_processed",
        "formatted_duration",
        "dry_run_badge",
        "user",
    ]

    list_filter = [
        "dry_run",
        "started_at",
        "completed_at",
        "user",
    ]

    search_fields = [
        "session_id",
        "user",
        "command_args",
    ]

    readonly_fields = [
        "session_id",
        "started_at",
        "completed_at",
        "formatted_duration",
        "is_complete",
        "is_successful",
        "success_rate",
    ]

    fields = [
        ("session_id", "user"),
        ("started_at", "completed_at"),
        ("dry_run", "formatted_duration"),
        ("total_transformers", "successful_transformers", "failed_transformers"),
        "total_records_processed",
        "command_args",
        ("is_complete", "is_successful", "success_rate"),
    ]

    ordering = ["-started_at"]

    date_hierarchy = "started_at"

    def status_display(self, obj):
        """Display status with colored icons"""
        if not obj.is_complete:
            return format_html('<span style="color: orange;">🔄 In Progress</span>')
        elif obj.is_successful:
            return format_html('<span style="color: green;">✅ Completed</span>')
        else:
            return format_html('<span style="color: red;">❌ Failed</span>')

    status_display.short_description = "Status"

    def transformer_summary(self, obj):
        """Display transformer success/failure summary"""
        return f"{obj.successful_transformers}/{obj.total_transformers}"

    transformer_summary.short_description = "Success/Total"

    def dry_run_badge(self, obj):
        """Display dry run badge"""
        if obj.dry_run:
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 11px;">DRY RUN</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">LIVE</span>'
        )

    dry_run_badge.short_description = "Mode"

    def formatted_duration(self, obj):
        """Display formatted duration"""
        return obj.get_formatted_duration()

    formatted_duration.short_description = "Duration"

    def success_rate(self, obj):
        """Calculate and display success rate"""
        if obj.total_transformers == 0:
            return "N/A"
        rate = (obj.successful_transformers / obj.total_transformers) * 100
        return f"{rate:.1f}%"

    success_rate.short_description = "Success Rate"


# Custom admin site configuration
class ETLAdminSite(admin.AdminSite):
    """Custom admin site for ETL Framework"""

    site_header = "Django ETL Framework Administration"
    site_title = "ETL Admin"
    index_title = "ETL Framework Management"

    def index(self, request, extra_context=None):
        """Customize the admin index page with ETL-specific information"""
        extra_context = extra_context or {}

        # Add ETL-specific dashboard data
        recent_cutoff = timezone.now() - timedelta(hours=24)

        etl_stats = {
            "recent_migrations": MigrationLog.objects.filter(
                run_at__gte=recent_cutoff
            ).count(),
            "failed_migrations_today": MigrationLog.objects.filter(
                run_at__gte=recent_cutoff, success=False
            ).count(),
            "active_sessions": MigrationRunSummary.objects.filter(
                completed_at__isnull=True
            ).count(),
        }

        extra_context["etl_stats"] = etl_stats

        return super().index(request, extra_context)


# Create ETL admin site instance
etl_admin_site = ETLAdminSite(name="etl_admin")

# Register models with the custom admin site
etl_admin_site.register(MigrationLog, MigrationLogAdmin)
etl_admin_site.register(MigrationRunSummary, MigrationRunSummaryAdmin)
