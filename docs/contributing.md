# Contributing

We welcome contributions to the Django ETL Framework! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** and add tests
5. **Run the test suite** to ensure everything works
6. **Submit a pull request** with a clear description

## 📋 Development Setup

### Prerequisites

- Python 3.8 or higher
- Django 3.2 or higher
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/django-etl.git
cd django-etl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev,database,monitoring,docs]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=django_etl --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with black
black django_etl/ tests/

# Check code style with flake8
flake8 django_etl/ tests/

# Type checking with mypy
mypy django_etl/

# Run all quality checks
pre-commit run --all-files
```

## 🏗️ Project Structure

```
django-etl/
├── django_etl/           # Main package
│   ├── __init__.py
│   ├── base.py          # BaseTransformer class
│   ├── config.py        # Configuration management
│   ├── profiler.py      # Performance profiling
│   ├── validators.py    # Data validation
│   └── management/      # Django management commands
├── tests/               # Test suite
├── docs/                # Documentation
├── examples/            # Example transformers
└── setup.py            # Package configuration
```

## 🎯 Types of Contributions

### 🐛 Bug Fixes

- **Search existing issues** first to avoid duplicates
- **Create an issue** describing the bug with:
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Environment details (Python/Django versions)
- **Include tests** that demonstrate the bug
- **Fix the bug** and ensure tests pass

### ✨ New Features

- **Discuss the feature** in an issue before implementing
- **Follow the existing patterns** in the codebase
- **Add comprehensive tests** for new functionality
- **Update documentation** for user-facing changes
- **Consider backward compatibility**

### 📚 Documentation

- **Fix typos and clarify** existing documentation
- **Add examples** for complex features
- **Improve API documentation** with better docstrings
- **Add tutorials** for common use cases

### 🏥 Healthcare-Specific Features

We especially welcome contributions related to:

- HIPAA compliance improvements
- Healthcare data validation rules
- Medical record transformation patterns
- Integration with healthcare systems
- Performance optimizations for large datasets

## 📝 Coding Standards

### Python Style

- Follow **PEP 8** style guidelines
- Use **Black** for code formatting (120 character line length)
- Use **type hints** for all functions and methods
- Write **descriptive variable names**
- Add **docstrings** for all public functions and classes

### Code Example

```python
from typing import List, Optional
from django_etl import BaseTransformer

class PatientTransformer(BaseTransformer):
    """Transform patient data from legacy system to new format.
    
    This transformer handles the migration of patient records,
    including data cleaning and validation.
    
    Attributes:
        batch_size: Number of records to process in each batch
        description: Human-readable description of the transformer
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.batch_size = 1000
        self.description = "Transform legacy patient records"
    
    def get_source_data(self) -> QuerySet:
        """Get patient records from legacy database.
        
        Returns:
            QuerySet of legacy patient records to transform
        """
        return LegacyPatient.objects.using('legacy').filter(active=True)
    
    def transform_batch(self, batch: List[LegacyPatient]) -> List[Patient]:
        """Transform a batch of legacy patients.
        
        Args:
            batch: List of legacy patient records
            
        Returns:
            List of transformed patient objects
            
        Raises:
            ValidationError: If patient data is invalid
        """
        patients = []
        
        for legacy_patient in batch:
            try:
                patient_data = self._extract_patient_data(legacy_patient)
                if self._validate_patient_data(patient_data):
                    patients.append(Patient(**patient_data))
            except Exception as e:
                self.add_error(f"Failed to transform patient {legacy_patient.id}: {e}")
        
        return patients
    
    def _extract_patient_data(self, legacy_patient: LegacyPatient) -> dict:
        """Extract and clean patient data from legacy record."""
        # Implementation details...
        pass
```

### Documentation Style

- Use **Google-style docstrings**
- Include **type information** in docstrings
- Add **examples** for complex functions
- Use **Markdown** for documentation files

## 🧪 Testing Guidelines

### Test Structure

```python
import pytest
from django.test import TestCase
from django_etl.config import ETLConfigManager

class TestETLConfigManager(TestCase):
    """Test ETL configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ETLConfigManager()
    
    def test_get_database_config_existing(self):
        """Test getting configuration for existing database."""
        # Arrange
        db_name = 'default'
        
        # Act
        config = self.config_manager.get_database_config(db_name)
        
        # Assert
        self.assertIsNotNone(config)
        self.assertEqual(config.name, db_name)
    
    def test_get_database_config_missing(self):
        """Test getting configuration for non-existent database."""
        # Arrange
        db_name = 'nonexistent'
        
        # Act
        config = self.config_manager.get_database_config(db_name)
        
        # Assert
        self.assertIsNone(config)
    
    @pytest.mark.parametrize("batch_size,expected", [
        (100, 100),
        (None, 1000),  # Default value
    ])
    def test_batch_size_configuration(self, batch_size, expected):
        """Test batch size configuration with various values."""
        # Test implementation...
        pass
```

### Test Coverage

- **Aim for 90%+ test coverage**
- **Test edge cases** and error conditions
- **Use mocks** for external dependencies
- **Test configuration variations**
- **Include integration tests**

### Healthcare Testing

For healthcare-specific features:

- **Use synthetic data** that resembles real healthcare data
- **Test HIPAA compliance** features thoroughly
- **Validate data anonymization** functions
- **Test large dataset performance**

## 🔄 Pull Request Process

### Before Submitting

1. **Update your branch** with the latest main branch
2. **Run the full test suite**
3. **Check code quality** with pre-commit hooks
4. **Update documentation** if needed
5. **Add changelog entry** for significant changes

### Pull Request Description

Include in your PR description:

- **Summary** of changes made
- **Motivation** for the changes
- **Testing** performed
- **Breaking changes** (if any)
- **Related issues** (use "Fixes #123" syntax)

### Example PR Description

```markdown
## Summary
Add support for PostgreSQL array fields in data validation

## Motivation  
Healthcare systems often use PostgreSQL array fields for storing multiple values (e.g., multiple diagnoses). The existing validation system didn't handle these fields properly.

## Changes
- Added `ArrayFieldValidator` class
- Extended `BaseTransformer` to handle array field validation
- Added configuration options for array field handling

## Testing
- Added unit tests for array field validation
- Tested with real PostgreSQL array data
- Added integration test with healthcare data

## Breaking Changes
None - this is backward compatible

## Related Issues
Fixes #145
```

### Code Review Process

1. **Automated checks** must pass (tests, linting)
2. **At least one maintainer** must review
3. **Address feedback** promptly
4. **Squash commits** if requested
5. **Maintainer merges** after approval

## 🏷️ Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible functionality
- **PATCH** version for backward-compatible bug fixes

### Changelog

Keep the changelog updated in `CHANGELOG.md`:

```markdown
## [1.2.0] - 2025-01-15

### Added
- PostgreSQL array field validation support
- New healthcare data validation rules
- Performance improvements for large datasets

### Changed
- Improved error messages in configuration validation
- Updated documentation with more examples

### Fixed
- Memory leak in batch processing
- Configuration validation for missing databases

### Deprecated
- Old YAML configuration system (will be removed in 2.0.0)
```

## 💬 Community Guidelines

### Communication

- **Be respectful** and professional
- **Use clear, descriptive** issue and PR titles
- **Provide context** for your requests
- **Help others** when you can

### Getting Help

- **Check documentation** first
- **Search existing issues** before creating new ones
- **Use appropriate labels** on issues
- **Provide minimal reproducible examples**

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please read it before contributing.

## 🎖️ Recognition

Contributors are recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **Documentation** for major feature additions

## 📞 Contact

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Email**: [etl-support@yourcompany.com](mailto:etl-support@yourcompany.com) for sensitive issues

## 🙏 Thank You

Thank you for contributing to the Django ETL Framework! Your contributions help make data migration easier for the Django and healthcare communities.

---

**Happy coding!** 🚀
