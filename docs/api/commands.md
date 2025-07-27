# Management Commands API

The Django ETL framework provides powerful management commands to analyze, execute, and manage your data transformations from the command line.

## Overview

The framework includes two main management commands:

1. **`etl`** - Analysis and validation utilities
2. **`migrate_legacy_data`** - Execute data transformations

These commands integrate with Django's management system and can be used in scripts, cron jobs, or CI/CD pipelines.

---

## ETL Analysis Command

The `etl` command provides utilities for analyzing your data before running transformations.

### Basic Usage

```bash
python manage.py etl <action> --table <table_name> [options]
```

### Available Actions

#### `analyze` - Table Quality Analysis

Analyzes data quality metrics for a table:

```bash
# Analyze a table's data quality
python manage.py etl analyze --table legacy_patients

# Analyze with specific database
python manage.py etl analyze --table legacy_patients --database legacy

# Save results to file
python manage.py etl analyze --table legacy_patients --output analysis_report.json
```

**Output includes:**
- Row count and column statistics
- Data type distribution
- Null value percentages
- Unique value counts
- Data quality score

#### `duplicates` - Find Duplicate Records

Identifies duplicate records based on specified columns:

```bash
# Find duplicates by email
python manage.py etl duplicates --table legacy_patients --columns email

# Find duplicates by multiple columns
python manage.py etl duplicates --table legacy_patients --columns "first_name,last_name,date_of_birth"

# Save duplicate analysis
python manage.py etl duplicates --table legacy_patients --columns email --output duplicates.json
```

**Output includes:**
- Number of duplicate groups
- Total duplicate records
- Specific duplicate record details

#### `preview` - Data Transformation Preview

Previews how data will look after transformation:

```bash
# Preview specific columns
python manage.py etl preview --table legacy_patients --columns "first_name,last_name,email"

# Limit preview results
python manage.py etl preview --table legacy_patients --columns "first_name,last_name" --limit 5

# Preview with custom database
python manage.py etl preview --table legacy_patients --columns email --database legacy --limit 20
```

**Output includes:**
- Sample of original data
- Suggested transformations
- Data format recommendations

#### `estimate` - Performance Estimation

Estimates transformation time and resource requirements:

```bash
# Estimate transformation time
python manage.py etl estimate --table legacy_patients

# Estimate with custom batch size
python manage.py etl estimate --table legacy_patients --batch-size 2000

# Estimate for specific database
python manage.py etl estimate --table legacy_patients --database legacy --batch-size 500
```

**Output includes:**
- Estimated processing time
- Memory requirements
- Recommended batch sizes
- Performance optimization suggestions

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--table` | Table name to analyze (required) | - |
| `--database` | Database alias to use | `default` |
| `--columns` | Comma-separated column list | - |
| `--limit` | Limit for preview results | `10` |
| `--batch-size` | Batch size for estimation | `1000` |
| `--output` | Save results to JSON file | Console output |

### Example Workflow

```bash
# 1. Analyze data quality
python manage.py etl analyze --table legacy_patients --output patient_analysis.json

# 2. Check for duplicates
python manage.py etl duplicates --table legacy_patients --columns "ssn" --output patient_duplicates.json

# 3. Preview transformation
python manage.py etl preview --table legacy_patients --columns "first_name,last_name,date_of_birth" --limit 20

# 4. Estimate performance
python manage.py etl estimate --table legacy_patients --batch-size 1000
```

---

## Migration Execution Command

The `migrate_legacy_data` command executes your data transformations with comprehensive logging and monitoring.

### Basic Usage

```bash
python manage.py migrate_legacy_data [options]
```

### Core Options

#### `--dry-run` - Test Mode

Run transformations without saving data:

```bash
# Test all transformers without committing changes
python manage.py migrate_legacy_data --dry-run

# Test specific transformers
python manage.py migrate_legacy_data --dry-run --only "patients,departments"
```

**Benefits:**
- Validate transformation logic
- Test data mappings
- Check for errors before production run
- Get performance estimates

#### `--only` - Selective Execution

Run only specific transformers:

```bash
# Run single transformer
python manage.py migrate_legacy_data --only patients

# Run multiple transformers
python manage.py migrate_legacy_data --only "departments,patients,appointments"
```

#### `--enable-rollback` - Rollback Protection

Control automatic rollback on failures:

```bash
# Enable rollback (default)
python manage.py migrate_legacy_data --enable-rollback

# Disable rollback for faster execution
python manage.py migrate_legacy_data --no-enable-rollback
```

### Logging Options

#### `--log-file` - File Logging

Save detailed logs to a file:

```bash
# Log to specific file
python manage.py migrate_legacy_data --log-file /var/log/etl/migration.log

# Log with timestamp in filename
python manage.py migrate_legacy_data --log-file "migration_$(date +%Y%m%d_%H%M%S).log"
```

#### `--log-level` - Verbosity Control

Set logging verbosity:

```bash
# Debug level (most verbose)
python manage.py migrate_legacy_data --log-level DEBUG

# Info level (default)
python manage.py migrate_legacy_data --log-level INFO

# Warning level (less verbose)
python manage.py migrate_legacy_data --log-level WARNING

# Error level (least verbose)
python manage.py migrate_legacy_data --log-level ERROR
```

### Performance Options

#### `--batch-size` - Override Batch Size

Customize batch processing size:

```bash
# Use smaller batches for memory-constrained systems
python manage.py migrate_legacy_data --batch-size 500

# Use larger batches for better performance
python manage.py migrate_legacy_data --batch-size 5000
```

#### `--transformer-paths` - Custom Discovery

Specify custom transformer locations:

```bash
# Single path
python manage.py migrate_legacy_data --transformer-paths "myapp.transformers"

# Multiple paths
python manage.py migrate_legacy_data --transformer-paths "myapp.transformers,otherapp.etl.transformers"
```

### Complete Command Examples

#### Development Testing

```bash
# Full test run with debug logging
python manage.py migrate_legacy_data \
    --dry-run \
    --log-level DEBUG \
    --log-file "test_migration.log"
```

#### Selective Production Run

```bash
# Run specific transformers with rollback protection
python manage.py migrate_legacy_data \
    --only "departments,patients" \
    --enable-rollback \
    --log-file "/var/log/etl/production_migration.log" \
    --log-level INFO \
    --batch-size 2000
```

#### High-Performance Migration

```bash
# Fast migration with large batches
python manage.py migrate_legacy_data \
    --batch-size 10000 \
    --log-level WARNING \
    --log-file "/var/log/etl/fast_migration.log"
```

#### Comprehensive Migration with Full Logging

```bash
# Complete migration with all features enabled
python manage.py migrate_legacy_data \
    --enable-rollback \
    --enable-validation \
    --log-level INFO \
    --log-file "/var/log/etl/full_migration_$(date +%Y%m%d_%H%M%S).log" \
    --batch-size 1000
```

### Command Output

The migration command provides comprehensive output:

#### Progress Information
```
Running 'patients' transformer with enhanced features...
2024-01-15 14:30:12 - migration.PatientTransformer - INFO - Extracting data from LegacyPatient
2024-01-15 14:30:12 - migration.PatientTransformer - INFO - Found 15000 records to process
2024-01-15 14:30:13 - migration.PatientTransformer - INFO - Processing batch 1 (1000 records)
```

#### Performance Metrics
```
Performance Summary:
  data_extraction: 0.245s avg (15 times)
  data_transformation: 0.123s avg (15 times)
  bulk_create: 0.089s avg (15 times)
```

#### Final Summary
```
Enhanced ETL migration complete in 45.67s: 3 successful, 0 failed
Total records processed: 15000

💡 Recommendations for 'patients':
  - Consider larger bulk_create batches for better performance
  - Database extraction is optimal
```

## Production Deployment Patterns

### Cron Job Setup

```bash
# Daily migration cron job
0 2 * * * cd /app && python manage.py migrate_legacy_data --log-file "/var/log/etl/daily_$(date +\%Y\%m\%d).log" --log-level INFO

# Weekly full migration with analysis
0 1 * * 0 cd /app && python manage.py etl analyze --table legacy_patients --output /var/log/etl/weekly_analysis.json && python manage.py migrate_legacy_data --log-file "/var/log/etl/weekly_migration.log"
```

### CI/CD Integration

```yaml
# GitLab CI example
test_migration:
  script:
    - python manage.py migrate_legacy_data --dry-run --log-level INFO
    - python manage.py etl analyze --table legacy_patients --output analysis.json
  artifacts:
    reports:
      - analysis.json

deploy_migration:
  script:
    - python manage.py migrate_legacy_data --log-file "production_migration.log" --batch-size 2000
  only:
    - main
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Migration entrypoint
ENTRYPOINT ["python", "manage.py", "migrate_legacy_data"]
```

```bash
# Run migration in Docker
docker run --rm -v $(pwd)/logs:/app/logs myapp:latest \
    --log-file "/app/logs/migration.log" \
    --batch-size 1000
```

### Monitoring Integration

```bash
# Send metrics to monitoring system
python manage.py migrate_legacy_data --log-file migration.log && \
curl -X POST http://monitoring.company.com/metrics \
  -d "migration_status=success&duration=$(tail -1 migration.log | grep -o '[0-9.]*s')"
```

## Error Handling and Troubleshooting

### Common Issues

#### Transformer Discovery Errors
```bash
# Error: No transformers discovered
# Solution: Specify transformer paths explicitly
python manage.py migrate_legacy_data --transformer-paths "myapp.transformers,myapp.etl"
```

#### Database Connection Issues
```bash
# Error: Database 'legacy' not configured
# Solution: Check your DATABASES setting and ETL_CONFIG
python manage.py etl analyze --table patients --database default  # Use different database
```

#### Memory Issues with Large Datasets
```bash
# Solution: Use smaller batch sizes
python manage.py migrate_legacy_data --batch-size 100 --log-level DEBUG
```

#### Permission Issues
```bash
# Error: Permission denied writing log file
# Solution: Use accessible location or run with appropriate permissions
python manage.py migrate_legacy_data --log-file "./migration.log"
```

### Debugging Commands

```bash
# Verbose debugging
python manage.py migrate_legacy_data --dry-run --log-level DEBUG --log-file debug.log

# Test single transformer
python manage.py migrate_legacy_data --dry-run --only patients --log-level DEBUG

# Analyze before migrating
python manage.py etl analyze --table legacy_patients --output analysis.json
python manage.py etl estimate --table legacy_patients --batch-size 1000
```

The management commands provide a complete command-line interface for your ETL operations, from analysis and testing to production deployment and monitoring.
