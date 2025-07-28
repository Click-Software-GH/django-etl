"""
Enhanced Django ETL Framework Management Command
Integrates with existing migrate_legacy_data command patterns
"""

import time
import logging
import sys
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django_etl.discovery import discover_transformers
from django_etl.config import ETLConfigManager

try:
    # Try to import MigrationLog from the project
    from apps.logs.models import MigrationLog
except ImportError:
    # Fallback if MigrationLog doesn't exist
    MigrationLog = None


class Command(BaseCommand):
    help = "Run legacy-to-new data transformers with enhanced ETL framework features"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run transformers without committing to the database",
        )
        parser.add_argument(
            "--only",
            type=str,
            help="Comma-separated list of transformer keys to run (e.g., departments)",
        )
        parser.add_argument(
            "--log-file",
            type=str,
            help="Optional: file path to log migration output",
        )
        parser.add_argument(
            "--log-level",
            type=str,
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Set the logging level (default: INFO)",
        )
        parser.add_argument(
            "--enable-rollback",
            action="store_true",
            default=True,
            help="Enable automatic rollback on failure (default: True)",
        )
        parser.add_argument(
            "--enable-validation",
            action="store_true",
            default=True,
            help="Enable data validation (default: True)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            help="Override default batch size for processing",
        )
        parser.add_argument(
            "--transformer-paths",
            type=str,
            help="Comma-separated list of transformer module paths",
        )

    def setup_logging(self, log_file=None, log_level="INFO"):
        """Setup structured logging for migrations"""
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level))

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Migration-specific logger
        migration_logger = logging.getLogger("migration")
        migration_logger.setLevel(getattr(logging, log_level))

        return migration_logger

    def discover_transformers_from_apps(self, transformer_paths=None):
        """Discover transformers from Django apps"""
        if transformer_paths:
            # Use paths provided via command line
            base_paths = [path.strip() for path in transformer_paths.split(",")]
        else:
            # First try to get configured paths from Django settings
            config_manager = ETLConfigManager()
            configured_paths = config_manager.get_transformer_discovery_paths()

            if configured_paths:
                base_paths = configured_paths
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Using configured transformer paths: {', '.join(configured_paths)}"
                    )
                )
            else:
                # Only fall back to auto-discovery if no paths are configured
                # and limit to apps that might actually have transformers
                base_paths = []

                # Look for apps that are likely to have transformers
                # (avoiding Django contrib apps and third-party packages)
                for app_config in apps.get_app_configs():
                    app_name = app_config.name

                    # Skip Django contrib apps and common third-party packages
                    if (
                        not app_name.startswith("django.contrib.")
                        and not app_name.startswith("rest_framework")
                        and not app_name.startswith("drf_")
                        and not app_name.startswith("corsheaders")
                        and app_name != "django_etl"  # Skip ourselves
                        and (
                            app_name.startswith("apps.")  # Project apps
                            or app_name.startswith("core")  # Core app
                            or "." not in app_name  # Top-level apps
                        )
                    ):
                        potential_paths = [
                            f"{app_name}.transformers",
                            f"{app_name}.etl.transformers",
                        ]
                        base_paths.extend(potential_paths)

                if base_paths:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No transformer paths configured. Auto-discovering from: {', '.join(base_paths)}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "No transformer paths found. Please configure TRANSFORMER_DISCOVERY_PATHS in your Django settings."
                        )
                    )
                    return {}

        try:
            return discover_transformers(base_paths)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Could not auto-discover transformers: {e}")
            )
            return {}

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        only = options["only"]
        log_file = options["log_file"]
        log_level = options["log_level"]
        enable_rollback = options["enable_rollback"]
        enable_validation = options["enable_validation"]
        batch_size = options["batch_size"]
        transformer_paths = options["transformer_paths"]

        # Setup logging
        logger = self.setup_logging(log_file, log_level)

        # Set discovery logger to INFO to see detailed discovery output
        discovery_logger = logging.getLogger("django_etl.discovery")
        discovery_logger.setLevel(logging.INFO)

        # Log migration start with enhanced features
        mode = "DRY RUN" if dry_run else "LIVE"
        logger.info(f"Starting enhanced ETL migration in {mode} mode")
        logger.info(f"Rollback enabled: {enable_rollback}")
        logger.info(f"Validation enabled: {enable_validation}")

        if batch_size:
            logger.info(f"Custom batch size: {batch_size}")

        if log_file:
            logger.info(f"Logging to file: {log_file}")

        # Discover transformers
        transformers = self.discover_transformers_from_apps(transformer_paths)

        if not transformers:
            error_msg = "No transformers discovered. Check your transformer paths or create transformers."
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
            return

        # Determine which transformers to run
        if only:
            keys = [key.strip() for key in only.split(",")]
            transformers_to_run = {
                key: transformers[key] for key in keys if key in transformers
            }
            if not transformers_to_run:
                error_msg = f"No valid transformers found for: {', '.join(keys)}"
                logger.error(error_msg)
                self.stderr.write(self.style.ERROR(error_msg))
                return
            logger.info(f"Running specific transformers: {', '.join(keys)}")
        else:
            transformers_to_run = transformers
            logger.info(f"Running all {len(transformers_to_run)} transformers")

        total_start_time = time.time()
        results = {}

        for key, TransformerClass in transformers_to_run.items():
            logger.info(f"Starting '{key}' transformer...")
            self.stdout.write(f"Running '{key}' transformer with enhanced features...")

            start_time = time.time()
            success = True
            error_message = ""
            duration = 0
            migration_summary = {}

            try:
                # Instantiate transformer with enhanced features
                transformer = TransformerClass()

                # Override batch size if specified
                if batch_size and hasattr(transformer, "config"):
                    transformer.config.batch_size = batch_size

                # Run with enhanced features
                result = transformer.safe_run(
                    dry_run=dry_run, enable_rollback=enable_rollback and not dry_run
                )

                duration = time.time() - start_time

                # Get comprehensive migration summary
                migration_summary = transformer.get_migration_summary()

                results[key] = {
                    "success": True,
                    "duration": duration,
                    "result": result,
                    "summary": migration_summary,
                }

                # Log detailed success information
                stats = migration_summary.get("statistics", {})
                msg = (
                    f"'{key}' completed successfully in {duration:.2f}s. "
                    f"Stats: {stats}"
                )
                logger.info(msg)
                self.stdout.write(self.style.SUCCESS(msg))

                # Show performance insights
                perf_report = migration_summary.get("performance_report", {})
                if perf_report.get("operations"):
                    self.stdout.write("Performance Summary:")
                    for operation, op_stats in perf_report["operations"].items():
                        self.stdout.write(
                            f"  {operation}: {op_stats.get('avg_time', 0):.3f}s avg "
                            f"({op_stats.get('count', 0)} times)"
                        )

            except Exception as e:
                success = False
                error_message = str(e)
                duration = time.time() - start_time

                results[key] = {
                    "success": False,
                    "duration": duration,
                    "error": error_message,
                }

                err_msg = f"'{key}' failed after {duration:.2f}s: {error_message}"
                logger.error(err_msg, exc_info=True)
                self.stderr.write(self.style.ERROR(err_msg))

            # Log the migration result to database if MigrationLog is available
            if MigrationLog and not dry_run:
                try:
                    MigrationLog.objects.create(
                        dry_run=dry_run,
                        duration_seconds=duration,
                        transformer=key,
                        success=success,
                        error_message=error_message if not success else None,
                        # Enhanced logging fields
                        statistics=migration_summary.get("statistics", {}),
                        performance_data=migration_summary.get(
                            "performance_report", {}
                        ),
                    )
                except Exception as log_error:
                    logger.warning(f"Could not log to database: {log_error}")

        # Final summary
        total_duration = time.time() - total_start_time
        successful = sum(1 for r in results.values() if r["success"])
        failed = len(results) - successful

        summary = (
            f"Enhanced ETL migration complete in {total_duration:.2f}s: "
            f"{successful} successful, {failed} failed"
        )

        logger.info(summary)

        # Show overall statistics
        total_records_processed = sum(
            r.get("summary", {}).get("statistics", {}).get("created", 0)
            for r in results.values()
            if r["success"]
        )

        if total_records_processed > 0:
            self.stdout.write(f"Total records processed: {total_records_processed}")

        if failed == 0:
            self.stdout.write(self.style.SUCCESS(summary))
        else:
            self.stdout.write(self.style.WARNING(summary))

        # Show recommendations if any
        for key, result in results.items():
            if result["success"] and "summary" in result:
                perf_report = result["summary"].get("performance_report", {})
                recommendations = perf_report.get("recommendations", [])
                if recommendations:
                    self.stdout.write(f"\n💡 Recommendations for '{key}':")
                    for rec in recommendations:
                        self.stdout.write(f"  - {rec}")
