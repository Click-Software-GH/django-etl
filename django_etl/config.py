"""
ETL Configuration Management System
Provides centralized configuration management for ETL operations
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    engine: str = "mysql"
    charset: str = "utf8mb4"
    timeout: int = 30
    pool_size: int = 10


@dataclass
class TransformationConfig:
    """Transformation-specific configuration"""
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
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5
    console_output: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""
    enable_profiling: bool = True
    enable_metrics: bool = True
    alert_on_errors: bool = True
    alert_email: Optional[str] = None
    webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None


@dataclass
class ETLConfig:
    """Main ETL configuration"""
    project_name: str
    environment: str = "development"
    
    # Sub-configurations
    databases: Dict[str, DatabaseConfig] = field(default_factory=dict)
    transformation: TransformationConfig = field(default_factory=TransformationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Paths
    backup_directory: str = "/tmp/etl_backups"
    temp_directory: str = "/tmp/etl_temp"
    log_directory: str = "/var/log/etl"
    
    # Feature flags
    enable_rollback: bool = True
    enable_dry_run: bool = True
    enable_parallel_transforms: bool = False
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ETLConfigManager:
    """Manages ETL configuration across environments"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._default_config_path()
        self.config: Optional[ETLConfig] = None
        self._load_config()
    
    def _default_config_path(self) -> str:
        """Get default configuration path"""
        return os.path.join(os.path.dirname(__file__), "config", "etl_config.yaml")
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            self.config = ETLConfig(project_name="UHMS-ETL")
            self._create_default_config()
            return
        
        with open(self.config_path, 'r') as f:
            if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        self.config = self._dict_to_config(config_data)
    
    def _dict_to_config(self, data: Dict[str, Any]) -> ETLConfig:
        """Convert dictionary to ETLConfig object"""
        # Parse database configurations
        databases = {}
        for db_name, db_data in data.get('databases', {}).items():
            databases[db_name] = DatabaseConfig(**db_data)
        
        # Parse other configurations
        transformation = TransformationConfig(**data.get('transformation', {}))
        logging_config = LoggingConfig(**data.get('logging', {}))
        monitoring = MonitoringConfig(**data.get('monitoring', {}))
        
        return ETLConfig(
            project_name=data.get('project_name', 'UHMS-ETL'),
            environment=data.get('environment', 'development'),
            databases=databases,
            transformation=transformation,
            logging=logging_config,
            monitoring=monitoring,
            backup_directory=data.get('backup_directory', '/tmp/etl_backups'),
            temp_directory=data.get('temp_directory', '/tmp/etl_temp'),
            log_directory=data.get('log_directory', '/var/log/etl'),
            enable_rollback=data.get('enable_rollback', True),
            enable_dry_run=data.get('enable_dry_run', True),
            enable_parallel_transforms=data.get('enable_parallel_transforms', False),
            custom_settings=data.get('custom_settings', {})
        )
    
    def _create_default_config(self) -> None:
        """Create default configuration file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        default_config = {
            'project_name': 'UHMS-ETL',
            'environment': 'development',
            'databases': {
                'legacy': {
                    'host': 'localhost',
                    'port': 3306,
                    'database': 'uhms_legacy',
                    'username': 'root',
                    'password': 'password',
                    'engine': 'mysql'
                },
                'target': {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'uhms_new',
                    'username': 'postgres',
                    'password': 'password',
                    'engine': 'postgresql'
                }
            },
            'transformation': {
                'batch_size': 1000,
                'max_retries': 3,
                'retry_delay': 5,
                'enable_validation': True,
                'validation_mode': 'strict'
            },
            'logging': {
                'level': 'INFO',
                'file_path': '/var/log/etl/etl.log',
                'console_output': True
            },
            'monitoring': {
                'enable_profiling': True,
                'enable_metrics': True,
                'alert_on_errors': True
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
    
    def get_database_config(self, db_name: str) -> Optional[DatabaseConfig]:
        """Get database configuration by name"""
        return self.config.databases.get(db_name) if self.config else None
    
    def get_transformation_config(self) -> TransformationConfig:
        """Get transformation configuration"""
        return self.config.transformation if self.config else TransformationConfig()
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        if not self.config:
            return
        
        # Update configuration object
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Save to file
        self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        if not self.config:
            return
        
        # Convert config to dictionary
        config_dict = self._config_to_dict(self.config)
        
        with open(self.config_path, 'w') as f:
            if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_dict, f, indent=2, default=str)
    
    def _config_to_dict(self, config: ETLConfig) -> Dict[str, Any]:
        """Convert ETLConfig to dictionary"""
        return {
            'project_name': config.project_name,
            'environment': config.environment,
            'databases': {
                name: {
                    'host': db.host,
                    'port': db.port,
                    'database': db.database,
                    'username': db.username,
                    'password': db.password,
                    'engine': db.engine,
                    'charset': db.charset,
                    'timeout': db.timeout,
                    'pool_size': db.pool_size
                }
                for name, db in config.databases.items()
            },
            'transformation': {
                'batch_size': config.transformation.batch_size,
                'max_retries': config.transformation.max_retries,
                'retry_delay': config.transformation.retry_delay,
                'enable_validation': config.transformation.enable_validation,
                'validation_mode': config.transformation.validation_mode,
                'cleanup_on_error': config.transformation.cleanup_on_error,
                'parallel_processing': config.transformation.parallel_processing,
                'max_workers': config.transformation.max_workers
            },
            'logging': {
                'level': config.logging.level,
                'format': config.logging.format,
                'file_path': config.logging.file_path,
                'max_file_size_mb': config.logging.max_file_size_mb,
                'backup_count': config.logging.backup_count,
                'console_output': config.logging.console_output
            },
            'monitoring': {
                'enable_profiling': config.monitoring.enable_profiling,
                'enable_metrics': config.monitoring.enable_metrics,
                'alert_on_errors': config.monitoring.alert_on_errors,
                'alert_email': config.monitoring.alert_email,
                'webhook_url': config.monitoring.webhook_url,
                'slack_channel': config.monitoring.slack_channel
            },
            'backup_directory': config.backup_directory,
            'temp_directory': config.temp_directory,
            'log_directory': config.log_directory,
            'enable_rollback': config.enable_rollback,
            'enable_dry_run': config.enable_dry_run,
            'enable_parallel_transforms': config.enable_parallel_transforms,
            'custom_settings': config.custom_settings
        }
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        if not self.config:
            issues.append("No configuration loaded")
            return issues
        
        # Validate database connections
        for db_name, db_config in self.config.databases.items():
            if not db_config.host:
                issues.append(f"Database '{db_name}' missing host")
            if not db_config.database:
                issues.append(f"Database '{db_name}' missing database name")
        
        # Validate directories
        directories = [
            self.config.backup_directory,
            self.config.temp_directory,
            self.config.log_directory
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create directory '{directory}': {e}")
        
        return issues


# Global configuration manager instance
config_manager = ETLConfigManager()
