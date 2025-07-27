# Installation

Get up and running with the Django ETL Framework in minutes.

## Requirements

- **Python**: 3.8 or higher
- **Django**: 3.2 or higher
- **Database**: MySQL, PostgreSQL, or SQLite

## Installation Methods

=== "From GitHub (Recommended)"

    Install the latest version directly from GitHub:

    ```bash
    pip install git+https://github.com/Click-Software-GH/django-etl.git
    ```

    Install a specific version or branch:

    ```bash
    # Specific version
    pip install git+https://github.com/Click-Software-GH/django-etl.git@v1.0.0
    
    # Main branch
    pip install git+https://github.com/Click-Software-GH/django-etl.git@main
    ```

=== "Development Installation"

    For development or if you want to modify the framework:

    ```bash
    # Clone the repository
    git clone https://github.com/Click-Software-GH/django-etl.git
    cd django-etl

    # Install in editable mode
    pip install -e .
    ```

=== "With Extra Dependencies"

    Install with additional features:

    ```bash
    # Database drivers
    pip install "git+https://github.com/Click-Software-GH/django-etl.git[database]"
    
    # Monitoring tools
    pip install "git+https://github.com/Click-Software-GH/django-etl.git[monitoring]"
    
    # All extras
    pip install "git+https://github.com/Click-Software-GH/django-etl.git[database,monitoring,async]"
    ```

## Extra Dependencies

| Extra | Includes | Use Case |
|-------|----------|----------|
| `database` | `psycopg2-binary`, `PyMySQL`, `cx-Oracle` | Database drivers |
| `monitoring` | `prometheus-client`, `grafana-api` | Performance monitoring |
| `async` | `aiofiles`, `asyncpg` | Async operations |
| `dev` | `pytest`, `black`, `flake8`, `mypy` | Development tools |
| `docs` | `mkdocs`, `mkdocs-material` | Documentation |

## Django Setup

### 1. Add to INSTALLED_APPS

Add the framework to your Django project:

```python
# settings.py
INSTALLED_APPS = [
    # ... your existing apps
    'django_etl',  # Add this line
]
```

### 2. Run Migrations

Create the necessary database tables:

```bash
python manage.py migrate django_etl
```

### 3. Basic Configuration

Add basic ETL configuration to your settings:

```python
# settings.py
ETL_CONFIG = {
    'PROJECT_NAME': 'My ETL Project',
    'TRANSFORMATION': {
        'BATCH_SIZE': 1000,
        'ENABLE_VALIDATION': True,
    },
    'REQUIRED_DATABASES': ['default'],
}
```

## Verify Installation

Test that everything is working correctly:

```python
# Test in Django shell
python manage.py shell

>>> import django_etl
>>> print(f"Django ETL Framework v{django_etl.__version__} installed!")
>>> from django_etl.config import config_manager
>>> print("Configuration loaded successfully!")
```

## Troubleshooting

### Common Issues

!!! warning "ImportError: No module named 'django_etl'"
    
    Make sure you've installed the package and it's in your Python path:
    
    ```bash
    pip list | grep django-etl
    ```

!!! warning "django.core.exceptions.ImproperlyConfigured"
    
    Ensure you've added `'django_etl'` to your `INSTALLED_APPS` and run migrations:
    
    ```bash
    python manage.py migrate django_etl
    ```

!!! warning "Database connection errors"
    
    Verify your Django `DATABASES` setting includes all databases you plan to use with ETL.

### Getting Help

If you encounter issues:

1. Check the [Configuration Guide](configuration.md)
2. Review [common examples](../examples/basic.md)
3. [Open an issue](https://github.com/Click-Software-GH/django-etl/issues) on GitHub
4. Email [etl-support@yourcompany.com](mailto:etl-support@yourcompany.com)

## Next Steps

- [Quick Start Guide](quickstart.md) - Create your first transformer
- [Configuration](configuration.md) - Configure the framework for your needs
- [User Guide](../user-guide/transformers.md) - Learn about transformers in detail

!!! tip "Ready for Production?"
    
    For production deployments, consider:
    
    - Setting up proper logging directories
    - Configuring monitoring and alerts  
    - Using environment variables for sensitive settings
    - Setting up database connection pooling
