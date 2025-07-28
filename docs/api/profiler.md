# Performance Profiler API

The profiler provides detailed performance monitoring and optimization suggestions for ETL operations.

## ETLProfiler

::: django_etl.profiler.ETLProfiler

## Usage Examples

### Basic Profiling

```python
from django_etl.profiler import ETLProfiler

# Create profiler instance
profiler = ETLProfiler()

# Profile an operation
with profiler.profile_operation("customer_transformation"):
    # Your ETL operation here
    for batch in customer_batches:
        process_customer_batch(batch)

# Get performance report
report = profiler.get_performance_report()
print(f"Operation took {report['operations']['customer_transformation']['avg_time']:.2f}s")
```

### Multiple Operations

```python
profiler = ETLProfiler()

# Profile multiple operations  
with profiler.profile_operation("data_extraction"):
    extract_data_from_source()

with profiler.profile_operation("data_transformation"):
    transform_extracted_data()

with profiler.profile_operation("data_loading"):
    load_data_to_target()

# Get comprehensive report
report = profiler.get_performance_report()
```

### Integration with BaseTransformer

The profiler is automatically integrated into the `BaseTransformer` class:

```python
from django_etl import BaseTransformer

class CustomerTransformer(BaseTransformer):
    def transform_batch(self, batch):
        # Profiling happens automatically
        customers = []
        for customer in batch:
            # Transformation logic
            customers.append(transformed_customer)
        return customers
```

## Performance Report Structure

The `get_performance_report()` method returns a comprehensive performance analysis:

```json
{
    "summary": {
        "total_time": 45.2,
        "total_operations": 156,
        "avg_operation_time": 0.29
    },
    "operations": {
        "customer_transformation": {
            "count": 50,
            "total_time": 25.5,
            "avg_time": 0.51,
            "min_time": 0.32,
            "max_time": 0.89,
            "avg_memory_delta": 12.5,
            "max_memory_delta": 45.2
        },
        "data_validation": {
            "count": 50,
            "total_time": 8.7,
            "avg_time": 0.17,
            "min_time": 0.10,
            "max_time": 0.35,
            "avg_memory_delta": 2.1,
            "max_memory_delta": 8.9
        }
    },
    "recommendations": [
        "Operation 'customer_transformation' is slow (avg: 0.5s). Consider optimization.",
        "Operation 'data_validation' uses high memory (max: 45.2MB). Consider batch processing."
    ]
}
```

## Optimization Suggestions

The profiler automatically generates optimization suggestions:

```python
profiler = ETLProfiler()

# ... perform operations ...

report = profiler.get_performance_report()
suggestions = profiler.suggest_optimizations(report)

for suggestion in suggestions:
    print(f"💡 {suggestion}")
```

Example suggestions:

- `Consider batch processing for customer_transformation`
- `Implement memory cleanup for data_loading`
- `Enable parallel processing for large datasets`
- `Reduce batch size to optimize memory usage`

## Memory Monitoring

The profiler tracks memory usage for each operation:

```python
# Memory usage is tracked automatically
with profiler.profile_operation("memory_intensive_task"):
    large_dataset = load_large_dataset()  # +150MB
    processed_data = process_dataset(large_dataset)  # +50MB
    del large_dataset  # -150MB

# Memory delta shows net change: +50MB
```

## Performance Thresholds

Configure custom thresholds for recommendations:

```python
class CustomETLProfiler(ETLProfiler):
    def suggest_optimizations(self, report):
        suggestions = []
        
        for operation, stats in report['operations'].items():
            # Custom slow operation threshold  
            if stats['avg_time'] > 1.0:  # 1 second
                suggestions.append(f"Optimize slow operation: {operation}")
            
            # Custom memory threshold
            if stats['max_memory_delta'] > 200:  # 200MB
                suggestions.append(f"Reduce memory usage: {operation}")
        
        return suggestions
```

## Logging Integration

The profiler integrates with Python's logging system:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

profiler = ETLProfiler()

# Operations are automatically logged
with profiler.profile_operation("data_processing"):
    process_data()

# Output: INFO:etl.profiler:data_processing: 2.34s, Memory: +15.2MB
```

## Production Monitoring

### Continuous Monitoring

```python
class MonitoredTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.profiler = ETLProfiler()
    
    def run(self):
        # Profile the entire transformation
        with self.profiler.profile_operation("full_transformation"):
            super().run()
        
        # Generate report
        report = self.profiler.get_performance_report()
        
        # Send alerts if performance degrades
        if report['summary']['avg_operation_time'] > 5.0:
            self.send_performance_alert(report)
```

### Performance Dashboards

Export metrics for monitoring dashboards:

```python
def export_metrics_to_prometheus(profiler):
    """Export profiler metrics to Prometheus"""

    report = profiler.get_performance_report()
    
    for operation, stats in report["operations"].items():
        # Export to Prometheus gauge
        operation_time_gauge.labels(operation=operation).set(stats["avg_time"])
        memory_usage_gauge.labels(operation=operation).set(stats['avg_memory_delta'])
```

## Configuration

Control profiler behavior through ETL configuration:

```python
# settings.py
ETL_CONFIG = {
    'MONITORING': {
        'ENABLE_PROFILING': True,
        'ENABLE_METRICS': True,
        'PERFORMANCE_THRESHOLD_SECONDS': 2.0,
        'MEMORY_THRESHOLD_MB': 100.0,
    }
}
```

## Best Practices

### 1. Granular Profiling

Profile specific operations for detailed insights:

```python
with profiler.profile_operation("database_query"):
    customers = Customer.objects.filter(active=True)

with profiler.profile_operation("data_cleaning"):
    cleaned_customers = [clean_customer(c) for c in customers]

with profiler.profile_operation("database_insert"):
    Customer.objects.bulk_create(cleaned_customers)
```

### 2. Memory Management

Monitor memory usage patterns:

```python
with profiler.profile_operation("batch_processing"):
    for batch in large_dataset_batches:
        with profiler.profile_operation("single_batch"):
            process_batch(batch)
        
        # Memory cleanup between batches
        gc.collect()
```

### 3. Performance Baselines

Establish performance baselines:

```python
def establish_baseline():
    profiler = ETLProfiler()
    
    # Run standard test dataset
    with profiler.profile_operation("baseline_test"):
        process_test_dataset()
    
    # Store baseline metrics
    baseline_report = profiler.get_performance_report()
    save_baseline_metrics(baseline_report)

def compare_to_baseline(current_report):
    baseline = load_baseline_metrics()
    
    for operation in current_report['operations']:
        current_time = current_report['operations'][operation]['avg_time']
        baseline_time = baseline['operations'][operation]['avg_time']
        
        if current_time > baseline_time * 1.5:  # 50% slower
            alert(f"Performance regression in {operation}")
```

### 4. Automated Optimization

Use profiler data for automatic optimization:

```python
class SelfOptimizingTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.profiler = ETLProfiler()
        self.batch_size = 1000
    
    def optimize_batch_size(self):
        report = self.profiler.get_performance_report()
        
        if 'batch_processing' in report['operations']:
            stats = report['operations']['batch_processing']
            
            # If memory usage is high, reduce batch size
            if stats['max_memory_delta'] > 200:
                self.batch_size = max(100, self.batch_size // 2)
                self.add_info(f"Reduced batch size to {self.batch_size} due to high memory usage")
            
            # If processing is fast and memory is low, increase batch size
            elif stats['avg_time'] < 1.0 and stats['max_memory_delta'] < 50:
                self.batch_size = min(5000, self.batch_size * 2)
                self.add_info(f"Increased batch size to {self.batch_size} for better performance")
```

The profiler is an essential tool for maintaining optimal ETL performance and identifying bottlenecks in your data transformation pipelines.
