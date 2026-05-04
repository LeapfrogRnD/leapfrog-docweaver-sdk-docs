"""System resource monitoring for auto-scaling metrics."""

import psutil

from utils.logger import log


class ResourceMonitor:
    """Monitor CPU and Memory usage for auto-scaling."""

    @staticmethod
    def get_memory_usage() -> float:
        """Get current memory usage percentage."""
        return psutil.virtual_memory().percent

    @staticmethod
    def get_cpu_usage() -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def get_all_metrics() -> dict[str, float]:
        """Get all resource metrics."""
        return {
            "memory_percent": ResourceMonitor.get_memory_usage(),
            "cpu_percent": ResourceMonitor.get_cpu_usage(),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        }

    @staticmethod
    def log_metrics():
        """Log current resource metrics."""
        metrics = ResourceMonitor.get_all_metrics()
        log.info(
            f"Resource Metrics - Memory: {metrics['memory_percent']:.1f}%, "
            f"CPU: {metrics['cpu_percent']:.1f}%, "
            f"Available: {metrics['memory_available_gb']:.2f}GB"
        )
        return metrics
