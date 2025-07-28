# Welcome to the Django ETL Framework documentation!

Django ETL Framework is a comprehensive, production-ready ETL (Extract, Transform, Load) framework specifically designed for Django applications.

The framework provides powerful tools for healthcare data migration and complex database transformations, with built-in HIPAA compliance patterns and medical data validation rules.

## Getting Started

The easiest way to understand what Django ETL Framework can do is to check out our [Quick Start Guide](getting-started/quickstart.md). In just a few minutes, you'll learn how to set up your first data transformation pipeline.

## Getting it

You can get Django ETL Framework by using pip:

```bash
$ pip install git+https://github.com/Click-Software-GH/django-etl.git
```

If you want to install it from source, grab the git repository and install:

```bash
$ git clone https://github.com/Click-Software-GH/django-etl.git
$ cd django-etl
$ pip install .
```

Then you will need to add the `django_etl` application to the INSTALLED_APPS setting of your Django project settings.py file.

For more detailed instructions check out our [Installation instructions](getting-started/installation.md). Enjoy.

## Compatibility with versions of Python and Django

We follow the Django guidelines for supported Python and Django versions:

- **Python**: 3.8+
- **Django**: 4.2+

This might mean the django-etl may work with older or unsupported versions but we do not guarantee it and most likely will not fix bugs related to incompatibilities with older versions.

## Key Features

- **Cross-Database Support** - MySQL, PostgreSQL, SQLite with automatic vendor detection
- **High Performance** - Memory-efficient batch processing with configurable batch sizes
- **Advanced Validation** - Healthcare-specific validation rules with severity levels
- **Performance Profiling** - Built-in monitoring and optimization recommendations
- **Rollback & Recovery** - Automatic backups and migration rollback capabilities
- **Comprehensive Logging** - Detailed audit trails and debugging information

## Contents

- [Installation instructions](getting-started/installation.md)
    - [Installing](getting-started/installation.md#installation-methods)
    - [Development](getting-started/installation.md#development-installation)
    - [Configuration](getting-started/installation.md#with-extra-dependencies)
- [Quick Start Guide](getting-started/quickstart.md)
    - [Define Your Models](getting-started/quickstart.md#step-2-define-your-models)
    - [Create Your First Transformer](getting-started/quickstart.md#step-3-create-your-first-transformer)
    - [Run Your Migration](getting-started/quickstart.md#step-4-run-your-migration)
- [Configuration](getting-started/configuration.md)
    - [Basic Configuration](getting-started/configuration.md#basic-configuration)
    - [Advanced Settings](getting-started/configuration.md#advanced-configuration)
    - [Environment Settings](getting-started/configuration.md#development-vs-production)
- [API Reference](api/)
    - [Configuration](api/config.md)
    - [Transformers](api/transformers.md)
    - [Management Commands](api/commands.md)
    - [Data Validation](api/validation.md)
    - [Rollback & Recovery](api/rollback.md)
    - [Performance Profiling](api/performance.md)
- [Migration Guide](migration-guide.md)
- [Contributing](contributing.md)

