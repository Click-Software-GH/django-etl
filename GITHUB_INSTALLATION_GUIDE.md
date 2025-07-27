# 🚀 GitHub Installation Guide

This document provides comprehensive instructions for installing the Django ETL Framework from GitHub in various scenarios.

## 📦 Installation Methods

### **Method 1: Direct GitHub Installation (Most Common)**

Install the latest version directly from GitHub:

```bash
# Install from main branch (latest)
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git

# Install specific version/tag
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.1.0

# Install from specific branch
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@develop
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@feature-branch

# Install with extra dependencies
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[database,monitoring]"
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[dev,database,docs]"
```

### **Method 2: Clone and Install for Development**

For contributors or when you need to modify the framework:

```bash
# Clone the repository
git clone https://github.com/Lsoldo-DEV/django-etl-framework.git
cd django-etl-framework

# Install in editable mode (changes reflect immediately)
pip install -e .

# Install with development dependencies
pip install -e .[dev,database,monitoring,docs]

# Install everything for full development setup
pip install -e .[dev,database,monitoring,docs,async]
```

### **Method 3: Private Repository Installation**

For private repositories or enterprise use:

```bash
# Using personal access token
pip install git+https://username:token@github.com/Lsoldo-DEV/django-etl-framework.git

# Using SSH (requires SSH key setup)
pip install git+ssh://git@github.com/Lsoldo-DEV/django-etl-framework.git

# From private fork
pip install git+https://github.com/yourcompany/django-etl-framework.git
```

### **Method 4: Requirements.txt Integration**

Add to your project's `requirements.txt`:

```txt
# requirements.txt

# Django ETL Framework from GitHub
git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0

# Or with extras
git+https://github.com/Lsoldo-DEV/django-etl-framework.git[database,monitoring]@main

# Your other dependencies
Django>=3.2,<5.0
psycopg2-binary>=2.9.0
```

Then install with:
```bash
pip install -r requirements.txt
```

### **Method 5: Pipenv/Poetry Integration**

#### With Pipenv:
```bash
# Add to Pipfile
pipenv install git+https://github.com/Lsoldo-DEV/django-etl-framework.git#egg=django-etl-framework

# Or specific version
pipenv install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0#egg=django-etl-framework"
```

#### With Poetry:
```bash
# Add to pyproject.toml
poetry add git+https://github.com/Lsoldo-DEV/django-etl-framework.git

# Or specific version
poetry add git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0
```

## 🏢 Team Installation Instructions

### For Team Members

Create a simple installation guide for your team:

```bash
# Team Installation Guide

## Quick Setup
1. Activate your virtual environment
2. Install the framework:
   pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0

3. Add to your Django settings:
   INSTALLED_APPS = [
       # ... your apps
       'django_etl',
   ]

4. Run migrations:
   python manage.py migrate django_etl

5. Test installation:
   python manage.py migrate_legacy_data --help
```

### For Different Environments

#### Development Environment
```bash
# Install with all development tools
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[dev,database,monitoring]@main"
```

#### Staging Environment
```bash
# Install specific tested version
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0
```

#### Production Environment
```bash
# Install stable release with minimal dependencies
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0
```

## 🔄 Version Management

### Installing Specific Versions

```bash
# Install by tag (recommended for production)
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.1.0

# Install by commit hash (for specific fixes)
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@abc123def

# Install by branch (for testing new features)  
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@feature-new-validation
```

### Updating the Framework

```bash
# Update to latest version
pip install --upgrade git+https://github.com/Lsoldo-DEV/django-etl-framework.git

# Update to specific version
pip install --upgrade git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.1.0

# Force reinstall (if having issues)
pip install --force-reinstall git+https://github.com/Lsoldo-DEV/django-etl-framework.git
```

## 🛠️ Extra Dependencies

The framework supports several optional dependency groups:

### Available Extras

```bash
# Database drivers
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[database]"
# Includes: psycopg2-binary, PyMySQL, cx-Oracle

# Development tools
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[dev]"
# Includes: pytest, black, flake8, mypy, pre-commit

# Documentation tools
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[docs]"
# Includes: mkdocs, mkdocs-material, mkdocstrings

# Monitoring capabilities
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[monitoring]"
# Includes: prometheus-client, grafana-api

# Async support
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[async]"
# Includes: aiofiles, asyncpg

# Install multiple extras
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[database,dev,monitoring]"

# Install everything
pip install "git+https://github.com/Lsoldo-DEV/django-etl-framework.git[database,dev,docs,monitoring,async]"
```

## 🔍 Verification

After installation, verify everything works:

```bash
# Check installation
pip show django-etl-framework

# Test basic import
python -c "
import django_etl
print(f'✅ Django ETL Framework v{django_etl.__version__} installed successfully!')
"

# Test management commands (after adding to INSTALLED_APPS)
python manage.py migrate_legacy_data --help
python manage.py etl --help
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Git Authentication Issues
```bash
# If you get authentication errors, try:
pip install git+https://username:token@github.com/Lsoldo-DEV/django-etl-framework.git

# Or setup SSH keys and use:
pip install git+ssh://git@github.com/Lsoldo-DEV/django-etl-framework.git
```

#### 2. Dependency Conflicts
```bash
# If you have dependency conflicts, try:
pip install --upgrade --force-reinstall git+https://github.com/Lsoldo-DEV/django-etl-framework.git

# Or create a fresh virtual environment:
python -m venv new_env
source new_env/bin/activate
pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git
```

#### 3. Import Errors
```bash
# Make sure django_etl is in INSTALLED_APPS
# Run migrations: python manage.py migrate django_etl
# Check Python path: python -c "import sys; print(sys.path)"
```

## 📋 Docker Installation

For containerized applications:

```dockerfile
# Dockerfile
FROM python:3.11

# Install the ETL framework
RUN pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git@v1.0.0

# Your app setup
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
```

## 🔐 Security Considerations

### For Private Repositories

1. **Use SSH keys** instead of tokens in production
2. **Limit token permissions** to read-only access
3. **Rotate tokens regularly**
4. **Use environment variables** for sensitive information

```bash
# Example with environment variable
export GITHUB_TOKEN="your_token_here"
pip install git+https://${GITHUB_TOKEN}@github.com/Lsoldo-DEV/django-etl-framework.git
```

## 📞 Support

If you encounter issues during installation:

1. **Check the repository**: [https://github.com/Lsoldo-DEV/django-etl-framework](https://github.com/Lsoldo-DEV/django-etl-framework)
2. **Create an issue**: For installation problems
3. **Check discussions**: For questions and tips
4. **Review documentation**: [Installation Success Guide](INSTALLATION_SUCCESS.md)

---

**Happy Installing! 🎉**
