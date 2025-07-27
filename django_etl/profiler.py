"""
ETL Performance Profiler
Provides detailed performance monitoring and optimization suggestions
"""

import time
import psutil
import logging
from collections import defaultdict
from typing import Dict, List, Any
from contextlib import contextmanager


class ETLProfiler:
    """Performance profiler for ETL operations"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_times = {}
        self.memory_usage = []
        self.logger = logging.getLogger("etl.profiler")
    
    @contextmanager
    def profile_operation(self, operation_name: str):
        """Context manager for profiling operations"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            yield self
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            self.metrics[operation_name].append({
                'duration': duration,
                'memory_start': start_memory,
                'memory_end': end_memory,
                'memory_delta': memory_delta,
                'timestamp': start_time
            })
            
            self.logger.info(f"{operation_name}: {duration:.2f}s, Memory: {memory_delta:+.1f}MB")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'summary': {},
            'operations': {},
            'recommendations': []
        }
        
        total_time = 0
        total_operations = 0
        
        for operation, measurements in self.metrics.items():
            if not measurements:
                continue
                
            durations = [m['duration'] for m in measurements]
            memory_deltas = [m['memory_delta'] for m in measurements]
            
            op_stats = {
                'count': len(measurements),
                'total_time': sum(durations),
                'avg_time': sum(durations) / len(durations),
                'min_time': min(durations),
                'max_time': max(durations),
                'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
                'max_memory_delta': max(memory_deltas)
            }
            
            report['operations'][operation] = op_stats
            total_time += op_stats['total_time']
            total_operations += op_stats['count']
            
            # Generate recommendations
            if op_stats['avg_time'] > 5:
                report['recommendations'].append(
                    f"Operation '{operation}' is slow (avg: {op_stats['avg_time']:.1f}s). Consider optimization."
                )
            
            if op_stats['max_memory_delta'] > 100:  # 100MB
                report['recommendations'].append(
                    f"Operation '{operation}' uses high memory (max: {op_stats['max_memory_delta']:.1f}MB). Consider batch processing."
                )
        
        report['summary'] = {
            'total_time': total_time,
            'total_operations': total_operations,
            'avg_operation_time': total_time / total_operations if total_operations > 0 else 0
        }
        
        return report
    
    def suggest_optimizations(self, report: Dict[str, Any]) -> List[str]:
        """Suggest performance optimizations based on profiling data"""
        suggestions = []
        
        for operation, stats in report['operations'].items():
            if stats['avg_time'] > 2:
                suggestions.append(f"Consider batch processing for {operation}")
            
            if stats['max_memory_delta'] > 50:
                suggestions.append(f"Implement memory cleanup for {operation}")
        
        return suggestions
