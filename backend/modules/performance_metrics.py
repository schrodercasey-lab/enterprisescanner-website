"""
Performance Monitoring for Phase 3 Modules
Tracks operation performance, generates metrics, and identifies bottlenecks
"""

import time
import threading
from functools import wraps
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import statistics
import logging

logger = logging.getLogger(__name__)


@dataclass
class OperationMetric:
    """Individual operation metric"""
    operation: str
    duration: float  # seconds
    success: bool
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationStats:
    """Statistics for an operation type"""
    operation: str
    count: int
    total_duration: float
    min_duration: float
    max_duration: float
    avg_duration: float
    median_duration: float
    p95_duration: float
    p99_duration: float
    success_rate: float
    errors: int


class PerformanceMonitor:
    """
    Track performance metrics for Phase 3 operations
    
    Features:
    - Automatic operation tracking
    - Statistical analysis
    - Percentile calculations
    - Success rate tracking
    - Time-window analysis
    """
    
    def __init__(self, retention_hours: int = 24):
        """
        Initialize performance monitor
        
        Args:
            retention_hours: Hours to retain metrics (default: 24)
        """
        self.metrics: Dict[str, List[OperationMetric]] = defaultdict(list)
        self.retention_hours = retention_hours
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def record_operation(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        metadata: Optional[Dict] = None
    ):
        """
        Record an operation metric
        
        Args:
            operation: Operation name (e.g., 'script_generation')
            duration: Duration in seconds
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        metric = OperationMetric(
            operation=operation,
            duration=duration,
            success=success,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        with self.lock:
            self.metrics[operation].append(metric)
    
    def get_statistics(
        self,
        operation: Optional[str] = None,
        minutes: Optional[int] = None
    ) -> Dict[str, OperationStats]:
        """
        Get performance statistics
        
        Args:
            operation: Specific operation name (None for all)
            minutes: Only include metrics from last N minutes (None for all)
            
        Returns:
            Dictionary of operation statistics
        """
        with self.lock:
            if operation:
                operations = {operation: self.metrics.get(operation, [])}
            else:
                operations = dict(self.metrics)
        
        # Filter by time window if specified
        if minutes:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            operations = {
                op: [m for m in metrics if m.timestamp >= cutoff_time]
                for op, metrics in operations.items()
            }
        
        # Calculate statistics
        stats = {}
        for op, metrics in operations.items():
            if not metrics:
                continue
            
            stats[op] = self._calculate_stats(op, metrics)
        
        return stats
    
    def _calculate_stats(
        self,
        operation: str,
        metrics: List[OperationMetric]
    ) -> OperationStats:
        """Calculate statistics from metrics"""
        durations = [m.duration for m in metrics]
        successes = [m.success for m in metrics]
        
        sorted_durations = sorted(durations)
        
        return OperationStats(
            operation=operation,
            count=len(metrics),
            total_duration=sum(durations),
            min_duration=min(durations) if durations else 0,
            max_duration=max(durations) if durations else 0,
            avg_duration=statistics.mean(durations) if durations else 0,
            median_duration=statistics.median(durations) if durations else 0,
            p95_duration=self._percentile(sorted_durations, 95),
            p99_duration=self._percentile(sorted_durations, 99),
            success_rate=(sum(successes) / len(successes) * 100) if successes else 0,
            errors=len([s for s in successes if not s])
        )
    
    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """Calculate percentile from sorted data"""
        if not sorted_data:
            return 0.0
        
        index = int(len(sorted_data) * percentile / 100)
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]
    
    def print_statistics(
        self,
        operation: Optional[str] = None,
        minutes: Optional[int] = None
    ):
        """
        Print formatted statistics
        
        Args:
            operation: Specific operation (None for all)
            minutes: Time window in minutes (None for all)
        """
        stats = self.get_statistics(operation, minutes)
        
        if not stats:
            print("No performance data available")
            return
        
        time_window = f" (last {minutes} minutes)" if minutes else ""
        print(f"\n{'='*80}")
        print(f"PHASE 3 PERFORMANCE STATISTICS{time_window}")
        print(f"{'='*80}\n")
        
        for op, stat in sorted(stats.items()):
            print(f"Operation: {op}")
            print(f"  Count:        {stat.count:,}")
            print(f"  Success Rate: {stat.success_rate:.2f}%")
            print(f"  Errors:       {stat.errors}")
            print(f"  Duration (ms):")
            print(f"    Min:        {stat.min_duration*1000:.2f}")
            print(f"    Avg:        {stat.avg_duration*1000:.2f}")
            print(f"    Median:     {stat.median_duration*1000:.2f}")
            print(f"    P95:        {stat.p95_duration*1000:.2f}")
            print(f"    P99:        {stat.p99_duration*1000:.2f}")
            print(f"    Max:        {stat.max_duration*1000:.2f}")
            print(f"  Total Time:   {stat.total_duration:.2f}s")
            print()
        
        print(f"{'='*80}\n")
    
    def get_slow_operations(
        self,
        threshold_ms: float = 1000,
        limit: int = 10
    ) -> List[OperationMetric]:
        """
        Get slowest operations
        
        Args:
            threshold_ms: Minimum duration in milliseconds
            limit: Maximum number of results
            
        Returns:
            List of slow operation metrics
        """
        threshold_sec = threshold_ms / 1000
        
        with self.lock:
            all_metrics = []
            for metrics in self.metrics.values():
                all_metrics.extend([
                    m for m in metrics 
                    if m.duration >= threshold_sec
                ])
        
        # Sort by duration descending
        all_metrics.sort(key=lambda m: m.duration, reverse=True)
        
        return all_metrics[:limit]
    
    def get_error_operations(self, limit: int = 10) -> List[OperationMetric]:
        """
        Get recent failed operations
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of failed operation metrics
        """
        with self.lock:
            all_metrics = []
            for metrics in self.metrics.values():
                all_metrics.extend([m for m in metrics if not m.success])
        
        # Sort by timestamp descending (most recent first)
        all_metrics.sort(key=lambda m: m.timestamp, reverse=True)
        
        return all_metrics[:limit]
    
    def clear_metrics(self, operation: Optional[str] = None):
        """
        Clear metrics
        
        Args:
            operation: Specific operation to clear (None for all)
        """
        with self.lock:
            if operation:
                self.metrics[operation].clear()
            else:
                self.metrics.clear()
        
        logger.info(f"Cleared metrics for: {operation or 'all operations'}")
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        with self.lock:
            for operation in self.metrics:
                self.metrics[operation] = [
                    m for m in self.metrics[operation]
                    if m.timestamp >= cutoff_time
                ]
    
    def _start_cleanup_thread(self):
        """Start background thread to cleanup old metrics"""
        def cleanup_loop():
            while True:
                time.sleep(3600)  # Run every hour
                try:
                    self._cleanup_old_metrics()
                except Exception as e:
                    logger.error(f"Metrics cleanup failed: {e}")
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
    
    def export_metrics(self) -> Dict[str, Any]:
        """
        Export metrics for external monitoring systems
        
        Returns:
            Dictionary suitable for JSON export
        """
        stats = self.get_statistics()
        
        export = {
            'timestamp': datetime.utcnow().isoformat(),
            'retention_hours': self.retention_hours,
            'operations': {}
        }
        
        for op, stat in stats.items():
            export['operations'][op] = {
                'count': stat.count,
                'success_rate': stat.success_rate,
                'errors': stat.errors,
                'avg_duration_ms': stat.avg_duration * 1000,
                'p95_duration_ms': stat.p95_duration * 1000,
                'p99_duration_ms': stat.p99_duration * 1000
            }
        
        return export


# Global singleton instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get singleton performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


# Decorator for automatic performance tracking
def track_performance(operation: str, metadata: Optional[Dict] = None):
    """
    Decorator to automatically track function performance
    
    Args:
        operation: Operation name
        metadata: Additional metadata to record
    
    Example:
        @track_performance('script_generation')
        def generate_script():
            # ... function code ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            finally:
                duration = time.time() - start_time
                monitor.record_operation(
                    operation=operation,
                    duration=duration,
                    success=success,
                    metadata=metadata or {}
                )
        
        return wrapper
    return decorator


# Context manager for performance tracking
class track_operation:
    """
    Context manager for tracking operation performance
    
    Example:
        with track_operation('config_generation'):
            # ... operation code ...
    """
    
    def __init__(self, operation: str, metadata: Optional[Dict] = None):
        self.operation = operation
        self.metadata = metadata or {}
        self.monitor = get_performance_monitor()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None
        
        self.monitor.record_operation(
            operation=self.operation,
            duration=duration,
            success=success,
            metadata=self.metadata
        )
        
        return False  # Don't suppress exceptions


if __name__ == "__main__":
    # Test performance monitoring
    monitor = get_performance_monitor()
    
    # Simulate some operations
    import random
    
    print("Simulating operations...")
    for i in range(100):
        # Script generation
        duration = random.uniform(0.001, 0.1)
        success = random.random() > 0.05  # 95% success rate
        monitor.record_operation('script_generation', duration, success)
        
        # Config generation
        duration = random.uniform(0.002, 0.15)
        success = random.random() > 0.03  # 97% success rate
        monitor.record_operation('config_generation', duration, success)
        
        # Monitoring checks
        duration = random.uniform(0.0001, 0.01)
        success = random.random() > 0.01  # 99% success rate
        monitor.record_operation('monitoring_check', duration, success)
    
    # Print statistics
    monitor.print_statistics()
    
    # Show slow operations
    print("Slow Operations (>50ms):")
    slow_ops = monitor.get_slow_operations(threshold_ms=50, limit=5)
    for op in slow_ops:
        print(f"  - {op.operation}: {op.duration*1000:.2f}ms at {op.timestamp}")
    
    # Show errors
    print("\nRecent Errors:")
    errors = monitor.get_error_operations(limit=5)
    for op in errors:
        print(f"  - {op.operation} failed at {op.timestamp}")
    
    print("\n✅ Performance monitoring test complete")
