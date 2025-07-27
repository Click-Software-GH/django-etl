# Performance Profiling API

The Django ETL framework includes built-in performance profiling to help you optimize your data transformations. The profiler tracks execution time, memory usage, and provides optimization recommendations.

## Overview

Performance profiling is automatically enabled when you use `BaseTransformer`. The profiler tracks:

- **Execution time** for each operation
- **Memory usage** and memory deltas  
- **Operation counts** and frequency
- **Performance bottlenecks** and slow operations

## Basic Usage

### Automatic Profiling in Transformers

All transformers automatically profile their operations:

```python
from django_etl.base import BaseTransformer

class PatientTransformer(BaseTransformer):
    def run(self):
        # All operations are automatically profiled
        for batch in self.extract_data(LegacyPatient):
            self.process_batch(batch)  # This is profiled
        
        # Get performance report
        report = self.get_performance_report()
        self.log_info(f"Total execution time: {report['summary']['total_time']:.2f}s")
```

### Manual Profiling

You can also profile specific operations manually:

```python
class CustomTransformer(BaseTransformer):
    def run(self):
        # Profile a specific operation
        with self.profiler.profile_operation("data_cleaning"):
            self.clean_patient_data()
        
        with self.profiler.profile_operation("validation_step"):
            self.validate_all_records()
        
        # Get detailed report
        report = self.profiler.get_performance_report()
```

### Standalone Profiler Usage

You can use the profiler outside of transformers:

```python
from django_etl.profiler import ETLProfiler

profiler = ETLProfiler()

# Profile database operations
with profiler.profile_operation("database_query"):
    results = Patient.objects.filter(status='active').count()

with profiler.profile_operation("bulk_insert"):
    Patient.objects.bulk_create(new_patients)

# Get results
report = profiler.get_performance_report()
print(f"Database query took: {report['operations']['database_query']['avg_time']:.2f}s")
```

## Performance Report Structure

### Getting a Performance Report

```python
transformer = PatientTransformer()
transformer.safe_run()

# Get comprehensive performance report
report = transformer.get_performance_report()
```

### Report Structure

The performance report contains three main sections:

```python
report = {
    'summary': {
        'total_time': 45.2,           # Total execution time in seconds
        'total_operations': 125,       # Number of profiled operations
        'avg_operation_time': 0.36     # Average time per operation
    },
    'operations': {
        'data_extraction': {
            'count': 10,              # Number of times this operation ran
            'total_time': 15.3,       # Total time for all occurrences
            'avg_time': 1.53,         # Average time per occurrence
            'min_time': 0.8,          # Fastest occurrence
            'max_time': 2.1,          # Slowest occurrence
            'avg_memory_delta': 25.4, # Average memory change in MB
            'max_memory_delta': 45.2  # Largest memory increase in MB
        },
        'data_transformation': { ... },
        'bulk_create': { ... }
    },
    'recommendations': [
        "Operation 'data_extraction' is slow (avg: 1.5s). Consider optimization.",
        "Operation 'bulk_create' uses high memory (max: 45.2MB). Consider batch processing."
    ]
}
```

## Using Performance Data

### Identifying Bottlenecks

```python
def analyze_performance(transformer):
    report = transformer.get_performance_report()
    
    # Find slowest operations
    operations = report['operations']
    slowest = max(operations.items(), key=lambda x: x[1]['avg_time'])
    print(f"Slowest operation: {slowest[0]} ({slowest[1]['avg_time']:.2f}s avg)")
    
    # Find memory-intensive operations
    memory_intensive = max(operations.items(), key=lambda x: x[1]['max_memory_delta'])
    print(f"Most memory-intensive: {memory_intensive[0]} ({memory_intensive[1]['max_memory_delta']:.1f}MB)")
    
    # Show recommendations
    for recommendation in report['recommendations']:
        print(f"💡 {recommendation}")
```

### Comparing Performance Across Runs

```python
class OptimizedPatientTransformer(BaseTransformer):
    def run(self):
        # Run transformation
        self.transform_patients()
        
        # Log performance comparison
        report = self.get_performance_report()
        self.log_performance_summary(report)
    
    def log_performance_summary(self, report):
        """Log key performance metrics"""
        summary = report['summary']
        self.log_info(f"Performance Summary:")
        self.log_info(f"  Total time: {summary['total_time']:.2f}s")
        self.log_info(f"  Operations: {summary['total_operations']}")
        self.log_info(f"  Avg per operation: {summary['avg_operation_time']:.3f}s")
        
        # Log top 3 slowest operations
        operations = sorted(
            report['operations'].items(),
            key=lambda x: x[1]['avg_time'],
            reverse=True
        )[:3]
        
        self.log_info("Slowest operations:")
        for name, stats in operations:
            self.log_info(f"  {name}: {stats['avg_time']:.2f}s avg ({stats['count']} times)")
```

## Optimization Based on Profiling

### Batch Size Optimization

```python
class OptimizedTransformer(BaseTransformer):
    def run(self):
        # Test different batch sizes
        batch_sizes = [500, 1000, 2000, 5000]
        best_batch_size = self.find_optimal_batch_size(batch_sizes)
        
        self.log_info(f"Using optimal batch size: {best_batch_size}")
        
        # Use optimal batch size for actual processing
        for batch in self.extract_data(LegacyPatient, batch_size=best_batch_size):
            with self.profiler.profile_operation("optimized_processing"):
                self.process_batch(batch)
    
    def find_optimal_batch_size(self, batch_sizes):
        """Test different batch sizes to find the optimal one"""
        test_data = list(LegacyPatient.objects.using('legacy')[:1000])  # Test data
        
        results = {}
        for batch_size in batch_sizes:
            with self.profiler.profile_operation(f"batch_test_{batch_size}"):
                # Process test batches
                for i in range(0, len(test_data), batch_size):
                    batch = test_data[i:i + batch_size]
                    self.process_test_batch(batch)
            
            # Get timing for this batch size
            report = self.profiler.get_performance_report()
            avg_time = report['operations'][f'batch_test_{batch_size}']['avg_time']
            results[batch_size] = avg_time
        
        # Return batch size with best performance
        return min(results.items(), key=lambda x: x[1])[0]
```

### Memory Usage Optimization

```python
class MemoryOptimizedTransformer(BaseTransformer):
    def run(self):
        # Monitor memory usage during processing
        for batch in self.extract_data(LegacyPatient, batch_size=1000):
            with self.profiler.profile_operation("memory_monitored_batch"):
                processed_data = self.process_batch(batch)
                
                # Check memory usage after processing
                report = self.profiler.get_performance_report()
                last_operation = report['operations']['memory_monitored_batch']
                
                if last_operation['memory_delta'] > 100:  # More than 100MB
                    self.log_warning("High memory usage detected, triggering cleanup")
                    self.cleanup_temp_data()
                    
                self.save_processed_data(processed_data)
                
                # Clear processed data to free memory
                del processed_data
```

### Database Operation Optimization

```python
class DatabaseOptimizedTransformer(BaseTransformer):
    def run(self):
        # Profile database operations separately
        with self.profiler.profile_operation("database_extraction"):
            legacy_data = self.extract_all_legacy_data()
        
        with self.profiler.profile_operation("in_memory_processing"):
            processed_data = self.process_data_in_memory(legacy_data)
        
        with self.profiler.profile_operation("bulk_database_insert"):
            self.bulk_insert_optimized(processed_data)
        
        # Analyze database performance
        self.analyze_database_performance()
    
    def analyze_database_performance(self):
        """Analyze database operation performance"""
        report = self.get_performance_report()
        
        db_extraction_time = report['operations']['database_extraction']['avg_time']
        processing_time = report['operations']['in_memory_processing']['avg_time']
        db_insert_time = report['operations']['bulk_database_insert']['avg_time']
        
        total_db_time = db_extraction_time + db_insert_time
        
        self.log_info(f"Performance Analysis:")
        self.log_info(f"  Database time: {total_db_time:.2f}s ({total_db_time/(total_db_time + processing_time)*100:.1f}%)")
        self.log_info(f"  Processing time: {processing_time:.2f}s ({processing_time/(total_db_time + processing_time)*100:.1f}%)")
        
        # Recommendations
        if db_extraction_time > processing_time * 2:
            self.log_warning("Database extraction is slow. Consider adding indexes or optimizing queries.")
        
        if db_insert_time > processing_time:
            self.log_warning("Database inserts are slow. Consider larger bulk_create batches.")
```

## Advanced Profiling Patterns

### Nested Operation Profiling

```python
class HierarchicalTransformer(BaseTransformer):
    def run(self):
        with self.profiler.profile_operation("full_migration"):
            self.migrate_departments()
            self.migrate_patients()
            self.migrate_appointments()
    
    def migrate_patients(self):
        with self.profiler.profile_operation("patient_migration"):
            for batch in self.extract_data(LegacyPatient):
                with self.profiler.profile_operation("patient_batch_processing"):
                    processed_patients = []
                    
                    for patient in batch:
                        with self.profiler.profile_operation("individual_patient_transform"):
                            processed_patient = self.transform_patient(patient)
                            processed_patients.append(processed_patient)
                    
                    with self.profiler.profile_operation("patient_batch_save"):
                        self.bulk_create_with_logging(Patient, processed_patients)
```

### Performance Regression Testing

```python
class RegressionTestTransformer(BaseTransformer):
    # Performance benchmarks (update these when you make optimizations)
    PERFORMANCE_BENCHMARKS = {
        'patient_migration': 2.0,      # Should complete in under 2 seconds
        'data_validation': 0.5,        # Should complete in under 0.5 seconds
        'bulk_create': 1.0,            # Should complete in under 1 second
    }
    
    def run(self):
        # Run normal transformation
        self.transform_data()
        
        # Check performance against benchmarks
        self.check_performance_regression()
    
    def check_performance_regression(self):
        """Check if performance has regressed"""
        report = self.get_performance_report()
        
        regressions = []
        for operation, benchmark in self.PERFORMANCE_BENCHMARKS.items():
            if operation in report['operations']:
                actual_time = report['operations'][operation]['avg_time']
                if actual_time > benchmark:
                    regression_pct = ((actual_time - benchmark) / benchmark) * 100
                    regressions.append(f"{operation}: {actual_time:.2f}s (expected <{benchmark}s, {regression_pct:.1f}% slower)")
        
        if regressions:
            self.log_warning("Performance regressions detected:")
            for regression in regressions:
                self.log_warning(f"  📉 {regression}")
        else:
            self.log_info("✅ All operations within performance benchmarks")
```

### Export Performance Data

```python
class PerformanceLoggingTransformer(BaseTransformer):
    def run(self):
        # Run transformation
        self.transform_data()
        
        # Export performance data for analysis
        self.export_performance_data()
    
    def export_performance_data(self):
        """Export performance data to JSON for external analysis"""
        import json
        from datetime import datetime
        
        report = self.get_performance_report()
        
        # Add metadata
        report['metadata'] = {
            'transformer': self.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'config': {
                'batch_size': self.config.batch_size,
                'max_retries': self.config.max_retries,
                'parallel_processing': getattr(self.config, 'parallel_processing', False)
            }
        }
        
        # Export to file
        filename = f"performance_{self.__class__.__name__}_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_info(f"Performance data exported to {filename}")
```

## Integration with Django Debug Toolbar

For development, you can integrate with Django Debug Toolbar:

```python
# settings.py (development)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    # ETL-specific debug settings
    ETL_CONFIG['LOGGING']['LEVEL'] = 'DEBUG'
    ETL_CONFIG['MONITORING']['ENABLE_PROFILING'] = True

# In your transformer
class DebugTransformer(BaseTransformer):
    def run(self):
        if settings.DEBUG:
            from django.db import connection
            queries_before = len(connection.queries)
        
        # Run transformation
        self.transform_data()
        
        if settings.DEBUG:
            queries_after = len(connection.queries)
            query_count = queries_after - queries_before
            
            report = self.get_performance_report()
            self.log_info(f"Debug Info:")
            self.log_info(f"  SQL queries executed: {query_count}")
            self.log_info(f"  Total time: {report['summary']['total_time']:.2f}s")
            self.log_info(f"  Time per query: {report['summary']['total_time']/query_count:.3f}s")
```

## Best Practices

### 1. Profile Early and Often

```python
# Always profile during development
transformer = MyTransformer()
transformer.safe_run(dry_run=True)  # Test run first

report = transformer.get_performance_report()
if report['summary']['total_time'] > 30:  # More than 30 seconds
    print("⚠ Transformer is slow, consider optimization")
```

### 2. Set Performance Budgets

```python
class BudgetedTransformer(BaseTransformer):
    PERFORMANCE_BUDGET = {
        'total_time': 60,      # Maximum 60 seconds total
        'memory_peak': 500,    # Maximum 500MB memory usage
        'avg_operation': 2     # Maximum 2 seconds per operation
    }
    
    def run(self):
        self.transform_data()
        self.check_performance_budget()
    
    def check_performance_budget(self):
        report = self.get_performance_report()
        
        if report['summary']['total_time'] > self.PERFORMANCE_BUDGET['total_time']:
            raise Exception(f"Performance budget exceeded: took {report['summary']['total_time']:.1f}s")
```

### 3. Monitor Production Performance

```python
# Use in production to track performance over time
class ProductionTransformer(BaseTransformer):
    def run(self):
        self.transform_data()
        
        # Send performance metrics to monitoring system
        report = self.get_performance_report()
        self.send_metrics_to_monitoring(report)
    
    def send_metrics_to_monitoring(self, report):
        # Example: Send to StatsD, CloudWatch, etc.
        import statsd
        client = statsd.StatsClient()
        
        client.timing('etl.total_time', report['summary']['total_time'] * 1000)
        client.gauge('etl.operations_count', report['summary']['total_operations'])
        
        for operation, stats in report['operations'].items():
            client.timing(f'etl.operation.{operation}', stats['avg_time'] * 1000)
```

The profiling system gives you detailed insights into your ETL performance, helping you optimize your transformations for production use.
