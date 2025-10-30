#!/usr/bin/env python3
"""
Metrics and telemetry system for repo-tickets.

Provides system monitoring, performance tracking, and health checks.
"""

from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from threading import RLock
import time
import json
from pathlib import Path

from .logging_utils import get_logger


logger = get_logger()


@dataclass
class MetricPoint:
    """Single metric data point."""
    
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


@dataclass
class OperationMetrics:
    """Metrics for a specific operation."""
    
    operation: str
    total_calls: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    error_count: int = 0
    last_called: Optional[datetime] = None
    
    @property
    def avg_duration_ms(self) -> float:
        """Calculate average duration."""
        if self.total_calls == 0:
            return 0.0
        return self.total_duration_ms / self.total_calls
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        if self.total_calls == 0:
            return 0.0
        return self.error_count / self.total_calls
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return 1.0 - self.error_rate
    
    def record(self, duration_ms: float, error: bool = False) -> None:
        """Record an operation execution."""
        self.total_calls += 1
        self.total_duration_ms += duration_ms
        self.min_duration_ms = min(self.min_duration_ms, duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)
        
        if error:
            self.error_count += 1
        
        self.last_called = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation': self.operation,
            'total_calls': self.total_calls,
            'total_duration_ms': self.total_duration_ms,
            'avg_duration_ms': self.avg_duration_ms,
            'min_duration_ms': self.min_duration_ms if self.min_duration_ms != float('inf') else 0,
            'max_duration_ms': self.max_duration_ms,
            'error_count': self.error_count,
            'error_rate': self.error_rate,
            'success_rate': self.success_rate,
            'last_called': self.last_called.isoformat() if self.last_called else None
        }


@dataclass
class SystemHealth:
    """System health status."""
    
    status: str  # healthy, degraded, unhealthy
    checks: Dict[str, bool] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    last_check: datetime = field(default_factory=datetime.now)
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.status == "healthy"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'status': self.status,
            'is_healthy': self.is_healthy,
            'checks': self.checks,
            'issues': self.issues,
            'last_check': self.last_check.isoformat()
        }


class MetricsCollector:
    """
    Collects and tracks system metrics.
    
    Features:
    - Operation timing
    - Error tracking
    - Performance monitoring
    - Resource usage
    - Bottleneck detection
    """
    
    def __init__(self, retention_minutes: int = 60):
        """
        Initialize metrics collector.
        
        Args:
            retention_minutes: How long to keep detailed metrics
        """
        self.retention_minutes = retention_minutes
        self._lock = RLock()
        
        # Operation metrics
        self.operations: Dict[str, OperationMetrics] = {}
        
        # Time series data (recent metrics)
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Counters
        self.counters: Dict[str, int] = defaultdict(int)
        
        # Gauges (current values)
        self.gauges: Dict[str, float] = {}
        
        # Start time
        self.started_at = datetime.now()
    
    def record_operation(
        self,
        operation: str,
        duration_ms: float,
        error: bool = False,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record an operation execution.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            error: Whether operation failed
            tags: Additional tags
        """
        with self._lock:
            # Get or create operation metrics
            if operation not in self.operations:
                self.operations[operation] = OperationMetrics(operation=operation)
            
            # Record metrics
            self.operations[operation].record(duration_ms, error)
            
            # Add to time series
            point = MetricPoint(
                name=f"operation.{operation}",
                value=duration_ms,
                timestamp=datetime.now(),
                tags=tags or {}
            )
            self.time_series[operation].append(point)
            
            # Increment counter
            self.counters[f"{operation}.calls"] += 1
            if error:
                self.counters[f"{operation}.errors"] += 1
            
            logger.debug(
                "Recorded operation metric",
                operation=operation,
                duration_ms=duration_ms,
                error=error
            )
    
    def increment(self, counter: str, value: int = 1) -> None:
        """Increment a counter."""
        with self._lock:
            self.counters[counter] += value
    
    def set_gauge(self, gauge: str, value: float) -> None:
        """Set a gauge value."""
        with self._lock:
            self.gauges[gauge] = value
    
    def get_operation_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Get operation metrics.
        
        Args:
            operation: Specific operation (all if None)
        
        Returns:
            Metrics dictionary
        """
        with self._lock:
            if operation:
                op_metrics = self.operations.get(operation)
                return op_metrics.to_dict() if op_metrics else {}
            
            return {
                op: metrics.to_dict()
                for op, metrics in self.operations.items()
            }
    
    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get slowest operations by average duration.
        
        Args:
            limit: Maximum number to return
        
        Returns:
            List of operation metrics
        """
        with self._lock:
            sorted_ops = sorted(
                self.operations.values(),
                key=lambda x: x.avg_duration_ms,
                reverse=True
            )
            
            return [op.to_dict() for op in sorted_ops[:limit]]
    
    def get_most_called_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently called operations."""
        with self._lock:
            sorted_ops = sorted(
                self.operations.values(),
                key=lambda x: x.total_calls,
                reverse=True
            )
            
            return [op.to_dict() for op in sorted_ops[:limit]]
    
    def get_error_prone_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get operations with highest error rates."""
        with self._lock:
            error_ops = [
                op for op in self.operations.values()
                if op.error_count > 0
            ]
            
            sorted_ops = sorted(
                error_ops,
                key=lambda x: x.error_rate,
                reverse=True
            )
            
            return [op.to_dict() for op in sorted_ops[:limit]]
    
    def get_counters(self) -> Dict[str, int]:
        """Get all counters."""
        with self._lock:
            return dict(self.counters)
    
    def get_gauges(self) -> Dict[str, float]:
        """Get all gauges."""
        with self._lock:
            return dict(self.gauges)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        with self._lock:
            total_calls = sum(op.total_calls for op in self.operations.values())
            total_errors = sum(op.error_count for op in self.operations.values())
            
            return {
                'uptime_seconds': (datetime.now() - self.started_at).total_seconds(),
                'total_operations': len(self.operations),
                'total_calls': total_calls,
                'total_errors': total_errors,
                'overall_error_rate': total_errors / total_calls if total_calls > 0 else 0.0,
                'counters_count': len(self.counters),
                'gauges_count': len(self.gauges)
            }
    
    def detect_bottlenecks(self, threshold_ms: float = 100.0) -> List[Dict[str, Any]]:
        """
        Detect performance bottlenecks.
        
        Args:
            threshold_ms: Operations slower than this are bottlenecks
        
        Returns:
            List of bottleneck operations
        """
        with self._lock:
            bottlenecks = []
            
            for op in self.operations.values():
                if op.avg_duration_ms > threshold_ms:
                    bottlenecks.append({
                        'operation': op.operation,
                        'avg_duration_ms': op.avg_duration_ms,
                        'total_calls': op.total_calls,
                        'severity': 'critical' if op.avg_duration_ms > threshold_ms * 5 else 'warning'
                    })
            
            return sorted(bottlenecks, key=lambda x: x['avg_duration_ms'], reverse=True)
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self.operations.clear()
            self.time_series.clear()
            self.counters.clear()
            self.gauges.clear()
            self.started_at = datetime.now()
            
            logger.info("Metrics reset")


class SystemMetrics:
    """
    High-level system metrics and health monitoring.
    
    Tracks overall system performance and health.
    """
    
    def __init__(self, collector: Optional[MetricsCollector] = None):
        """
        Initialize system metrics.
        
        Args:
            collector: MetricsCollector instance
        """
        self.collector = collector or MetricsCollector()
        self._health_checks: Dict[str, Callable[[], bool]] = {}
    
    def register_health_check(self, name: str, check_fn: Callable[[], bool]) -> None:
        """
        Register a health check function.
        
        Args:
            name: Check name
            check_fn: Function that returns True if healthy
        """
        self._health_checks[name] = check_fn
        logger.debug(f"Registered health check: {name}")
    
    def check_health(self) -> SystemHealth:
        """
        Run all health checks.
        
        Returns:
            SystemHealth status
        """
        health = SystemHealth(status="healthy")
        
        for name, check_fn in self._health_checks.items():
            try:
                result = check_fn()
                health.checks[name] = result
                
                if not result:
                    health.issues.append(f"{name} check failed")
                    health.status = "degraded"
                    
            except Exception as e:
                health.checks[name] = False
                health.issues.append(f"{name} check error: {str(e)}")
                health.status = "unhealthy"
                
                logger.error(
                    "Health check failed",
                    check=name,
                    error=str(e)
                )
        
        # Check for critical issues
        if len(health.issues) > 3:
            health.status = "unhealthy"
        
        health.last_check = datetime.now()
        
        return health
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report.
        
        Returns:
            Performance report
        """
        summary = self.collector.get_summary()
        slowest = self.collector.get_slowest_operations(5)
        most_called = self.collector.get_most_called_operations(5)
        errors = self.collector.get_error_prone_operations(5)
        bottlenecks = self.collector.detect_bottlenecks()
        health = self.check_health()
        
        return {
            'summary': summary,
            'health': health.to_dict(),
            'slowest_operations': slowest,
            'most_called_operations': most_called,
            'error_prone_operations': errors,
            'bottlenecks': bottlenecks,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_metrics(self, file_path: Path) -> None:
        """
        Export metrics to file.
        
        Args:
            file_path: Output file path
        """
        report = self.get_performance_report()
        
        try:
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("Exported metrics", file=str(file_path))
            
        except Exception as e:
            logger.error("Failed to export metrics", error=str(e))


# Global metrics instance

_global_collector: Optional[MetricsCollector] = None
_global_system_metrics: Optional[SystemMetrics] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    global _global_collector
    
    if _global_collector is None:
        _global_collector = MetricsCollector()
    
    return _global_collector


def get_system_metrics() -> SystemMetrics:
    """Get global system metrics instance."""
    global _global_system_metrics
    
    if _global_system_metrics is None:
        _global_system_metrics = SystemMetrics(get_metrics_collector())
    
    return _global_system_metrics


def record_operation(
    operation: str,
    duration_ms: float,
    error: bool = False,
    tags: Optional[Dict[str, str]] = None
) -> None:
    """
    Record an operation to global metrics.
    
    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        error: Whether operation failed
        tags: Additional tags
    """
    collector = get_metrics_collector()
    collector.record_operation(operation, duration_ms, error, tags)


# Context manager for timing operations

class timed_operation:
    """
    Context manager for timing operations with metrics.
    
    Usage:
        with timed_operation("load_ticket"):
            ticket = storage.load_ticket(ticket_id)
    """
    
    def __init__(self, operation: str, tags: Optional[Dict[str, str]] = None):
        """
        Initialize timer.
        
        Args:
            operation: Operation name
            tags: Additional tags
        """
        self.operation = operation
        self.tags = tags or {}
        self.start_time = None
        self.error = False
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record metric."""
        duration_ms = (time.time() - self.start_time) * 1000
        self.error = exc_type is not None
        
        record_operation(self.operation, duration_ms, self.error, self.tags)
        
        return False  # Don't suppress exceptions


__all__ = [
    'MetricPoint',
    'OperationMetrics',
    'SystemHealth',
    'MetricsCollector',
    'SystemMetrics',
    'get_metrics_collector',
    'get_system_metrics',
    'record_operation',
    'timed_operation',
]
