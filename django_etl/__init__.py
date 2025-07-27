"""
Django ETL Framework
A comprehensive Django-based ETL framework with advanced features including:
- Enhanced BaseTransformer with validation, profiling, and rollback
- Healthcare-specific validation rules
- Performance monitoring and optimization
- Multi-database compatibility (MySQL, PostgreSQL, SQLite)
- Migration tracking and logging
- Configuration management
"""

# Version info
__version__ = "1.0.0"
__author__ = "ETL Framework Team"

# Default app configuration
default_app_config = "django_etl.apps.DjangoEtlConfig"

# Import main components for easy access
from .base import BaseTransformer

__all__ = [
    "BaseTransformer",
    "__version__",
]
