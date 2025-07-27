"""
ETL Configuration Management System
Provides centralized configuration management for ETL operations using Django settings
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@dataclass
class DatabaseConfig:
    """Database configuration from Django DATABASES setting"""

    name: str
    engine: str
    host: str
    port: int
    database: str
    user: str
    password: str

    @classmethod
    def from_django_db_config(
        cls, db_name: str, db_config: Dict[str, Any]
    ) -> "DatabaseConfig":
        """Create DatabaseConfig from Django DATABASES configuration"""
        return cls(
            name=db_name,
            engine=db_config.get("ENGINE", ""),
            host=db_config.get("HOST", "localhost"),
            port=int(db_config.get("PORT", 5432)),
            database=db_config.get("NAME", ""),
            user=db_config.get("USER", ""),
            password=db_config.get("PASSWORD", ""),
        )


@dataclass
class TransformationConfig:
    """Transformation-specific configuration from Django settings"""

    batch_size: int = 1000
    max_retries: int = 3
    retry_delay: int = 5
    enable_validation: bool = True
    validation_mode: str = "strict"  # strict, lenient, warning_only
    cleanup_on_error: bool = True
    parallel_processing: bool = False
    max_workers: int = 4


@dataclass
class LoggingConfig:
    """Logging configuration from Django settings"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5
    console_output: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration from Django settings"""

    enable_profiling: bool = True
    enable_metrics: bool = True
    alert_on_errors: bool = True
    alert_email: Optional[str] = None
    webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None


class ETLConfigManager:
    """Django-native ETL configuration manager that uses Django settings"""

    def __init__(self):
        self._etl_settings = getattr(settings, "ETL_CONFIG", {})
        self._validate_django_config()

    def _validate_django_config(self) -> None:
        """Validate ETL configuration against Django settings"""
        # Ensure we have Django settings available
        if not hasattr(settings, "DATABASES"):
            raise ImproperlyConfigured("Django DATABASES setting is required")

    def get_database_config(self, db_name: str) -> Optional[DatabaseConfig]:
        """Get database configuration from Django DATABASES setting"""
        if db_name not in settings.DATABASES:
            return None

        db_config = settings.DATABASES[db_name]
        return DatabaseConfig.from_django_db_config(db_name, db_config)

    def get_transformation_config(self) -> TransformationConfig:
        """Get transformation configuration from Django ETL_CONFIG setting"""
        transform_settings = self._etl_settings.get("TRANSFORMATION", {})

        return TransformationConfig(
            batch_size=transform_settings.get("BATCH_SIZE", 1000),
            max_retries=transform_settings.get("MAX_RETRIES", 3),
            retry_delay=transform_settings.get("RETRY_DELAY", 5),
            enable_validation=transform_settings.get("ENABLE_VALIDATION", True),
            validation_mode=transform_settings.get("VALIDATION_MODE", "strict"),
            cleanup_on_error=transform_settings.get("CLEANUP_ON_ERROR", True),
            parallel_processing=transform_settings.get("PARALLEL_PROCESSING", False),
            max_workers=transform_settings.get("MAX_WORKERS", 4),
        )

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration from Django ETL_CONFIG setting"""
        logging_settings = self._etl_settings.get("LOGGING", {})

        return LoggingConfig(
            level=logging_settings.get("LEVEL", "INFO"),
            format=logging_settings.get(
                "FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            file_path=logging_settings.get("FILE_PATH"),
            max_file_size_mb=logging_settings.get("MAX_FILE_SIZE_MB", 100),
            backup_count=logging_settings.get("BACKUP_COUNT", 5),
            console_output=logging_settings.get("CONSOLE_OUTPUT", True),
        )

    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration from Django ETL_CONFIG setting"""
        monitoring_settings = self._etl_settings.get("MONITORING", {})

        return MonitoringConfig(
            enable_profiling=monitoring_settings.get("ENABLE_PROFILING", True),
            enable_metrics=monitoring_settings.get("ENABLE_METRICS", True),
            alert_on_errors=monitoring_settings.get("ALERT_ON_ERRORS", True),
            alert_email=monitoring_settings.get("ALERT_EMAIL"),
            webhook_url=monitoring_settings.get("WEBHOOK_URL"),
            slack_channel=monitoring_settings.get("SLACK_CHANNEL"),
        )

    @property
    def project_name(self) -> str:
        """Get project name from Django settings"""
        return self._etl_settings.get(
            "PROJECT_NAME", getattr(settings, "PROJECT_NAME", "Django-ETL")
        )

    @property
    def environment(self) -> str:
        """Get environment from Django settings"""
        return self._etl_settings.get(
            "ENVIRONMENT", getattr(settings, "ENVIRONMENT", "development")
        )

    @property
    def backup_directory(self) -> str:
        """Get backup directory from Django settings"""
        default_backup = os.path.join(
            getattr(settings, "BASE_DIR", "/tmp"), "etl_backups"
        )
        return self._etl_settings.get("BACKUP_DIRECTORY", default_backup)

    @property
    def temp_directory(self) -> str:
        """Get temp directory from Django settings"""
        default_temp = os.path.join(getattr(settings, "BASE_DIR", "/tmp"), "etl_temp")
        return self._etl_settings.get("TEMP_DIRECTORY", default_temp)

    @property
    def log_directory(self) -> str:
        """Get log directory from Django settings"""
        default_log = os.path.join(getattr(settings, "BASE_DIR", "/tmp"), "logs", "etl")
        return self._etl_settings.get("LOG_DIRECTORY", default_log)

    @property
    def enable_rollback(self) -> bool:
        """Get rollback setting from Django settings"""
        return self._etl_settings.get("ENABLE_ROLLBACK", True)

    @property
    def enable_dry_run(self) -> bool:
        """Get dry run setting from Django settings"""
        return self._etl_settings.get("ENABLE_DRY_RUN", True)

    @property
    def enable_parallel_transforms(self) -> bool:
        """Get parallel transforms setting from Django settings"""
        return self._etl_settings.get("ENABLE_PARALLEL_TRANSFORMS", False)

    def get_transformer_discovery_paths(self) -> List[str]:
        """Get transformer discovery paths from Django settings"""
        return self._etl_settings.get("TRANSFORMER_DISCOVERY_PATHS", [])

    def validate_config(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []

        # Validate required Django settings
        if not hasattr(settings, "DATABASES"):
            issues.append("Django DATABASES setting is required")
            return issues

        # Validate database connections
        required_dbs = self._etl_settings.get("REQUIRED_DATABASES", ["default"])
        for db_name in required_dbs:
            if db_name not in settings.DATABASES:
                issues.append(
                    f"Required database '{db_name}' not configured in Django DATABASES"
                )
            else:
                db_config = settings.DATABASES[db_name]
                if not db_config.get("NAME"):
                    issues.append(
                        f"Database '{db_name}' missing NAME in Django DATABASES"
                    )

        # Validate directories
        directories = [self.backup_directory, self.temp_directory, self.log_directory]

        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create directory '{directory}': {e}")

        return issues


# Global configuration manager instance
config_manager = ETLConfigManager()
