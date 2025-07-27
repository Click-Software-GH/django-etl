from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


# Read requirements
def read_requirements(filename):
    """Read requirements from file"""
    requirements = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            requirements = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return requirements


setup(
    name="django-etl-framework",
    version="1.0.0",
    author="ETL Framework Team",
    author_email="etl-team@example.com",
    description="A comprehensive Django-based ETL framework with advanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Click-Software-GH/django-etl",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2,<5.0",
        "PyYAML>=6.0",
        "psutil>=5.9.0",
        "python-dateutil>=2.8.0",
        "Pillow>=8.0.0",  # For any image processing if needed
        "openpyxl>=3.0.0",  # For Excel file processing
        "pandas>=1.3.0",  # For data processing and analysis
        "numpy>=1.21.0",  # Scientific computing support
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-django>=4.5.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.950",
            "pre-commit>=2.17.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.0.0",
            "mkdocstrings[python]>=0.19.0",
        ],
        "database": [
            "psycopg2-binary>=2.9.0",  # PostgreSQL
            "PyMySQL>=1.0.0",  # MySQL
            "cx-Oracle>=8.3.0",  # Oracle (optional)
        ],
        "monitoring": [
            "prometheus-client>=0.14.0",
            "grafana-api>=1.0.0",
        ],
        "async": [
            "aiofiles>=0.8.0",
            "asyncpg>=0.25.0",  # Async PostgreSQL
        ],
    },
    include_package_data=True,
    package_data={
        "django_etl": [
            "templates/django_etl/*.html",
            "static/django_etl/css/*.css",
            "static/django_etl/js/*.js",
            "config/*.yaml",
            "config/*.json",
        ],
    },
    entry_points={
        "console_scripts": [
            "django-etl=django_etl.cli:main",
        ],
    },
    keywords=[
        "django",
        "etl",
        "data-migration",
        "data-transformation",
        "healthcare",
        "database",
        "mysql",
        "postgresql",
        "validation",
        "profiling",
        "rollback",
        "batch-processing",
    ],
    project_urls={
        "Bug Reports": "https://github.com/Click-Software-GH/django-etl/issues",
        "Source": "https://github.com/Click-Software-GH/django-etl",
        # "Documentation": "https://django-etl-framework.readthedocs.io/",
    },
)
