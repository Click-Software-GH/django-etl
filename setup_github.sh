#!/bin/bash

# GitHub Repository Setup Script for Django ETL Framework

echo "🚀 Setting up Django ETL Framework for GitHub..."

# Navigate to the framework directory
cd /home/apollo/Workspace/projects/backend/django_etl_framework

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
else
    echo "📁 Git repository already exists"
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Django ETL Framework v1.0.0

🚀 Features:
- Cross-database ETL framework for Django (MySQL, PostgreSQL, SQLite)
- Healthcare-specific validation and transformations  
- Performance profiling and monitoring with memory tracking
- Rollback and recovery capabilities with automatic snapshots
- Comprehensive management commands (migrate_legacy_data, etl)
- Django admin integration with detailed migration tracking
- Multi-project support with easy installation
- Advanced validation framework with severity levels
- Batch processing with configurable sizes
- Comprehensive logging and error handling

🏥 Healthcare Focus:
- HIPAA-compliant data handling patterns
- Medical record transformations and validations
- Insurance and billing data migration support
- Patient, appointment, and staff data transformations

🔧 Technical Capabilities:
- Memory-efficient batch processing
- Foreign key mapping and relationship handling
- Duplicate detection and resolution
- Data quality analysis and reporting
- Performance benchmarking and optimization
- Automatic transformer discovery
- Dry-run testing capabilities

Ready for production use in healthcare and enterprise applications.
Built with ❤️ for the Django and Healthcare communities."

echo "✅ Repository setup complete!"
echo ""
echo "🌐 Next steps:"
echo "1. Create a new repository on GitHub named 'django-etl-framework'"
echo "2. Add the remote origin:"
echo "   git remote add origin https://github.com/Lsoldo-DEV/django-etl-framework.git"
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📦 Then anyone can install from GitHub with:"
echo "   pip install git+https://github.com/Lsoldo-DEV/django-etl-framework.git"
echo ""
echo "🏷️ Don't forget to create releases/tags for version management:"
echo "   git tag -a v1.0.0 -m 'Version 1.0.0: Initial release'"
echo "   git push origin v1.0.0"
