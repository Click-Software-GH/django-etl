# django_etl_framework/django_etl/apps.py
from django.apps import AppConfig


class DjangoEtlConfig(AppConfig):
    """Django ETL Framework app configuration"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_etl"
    verbose_name = "Django ETL Framework"

    def ready(self):
        """Initialize the ETL framework when Django starts"""
        # Import signal handlers, if any
        pass
