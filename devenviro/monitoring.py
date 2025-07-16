"""Error tracking and monitoring utilities"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import json


class ErrorTracker:
    """Simple error tracking and logging system"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        """Configure logging with file and console handlers"""
        log_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an error with context information"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }

        self.logger.error(f"Error occurred: {error_data}")

        # Save detailed error to JSON file
        error_file = self.log_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, "w") as f:
            json.dump(error_data, f, indent=2)

    def log_performance(self, operation: str, duration: float, metadata: Optional[Dict] = None):
        """Log performance metrics"""
        perf_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration_seconds": duration,
            "metadata": metadata or {},
        }

        self.logger.info(f"Performance: {operation} took {duration:.2f}s")

        # Append to performance log
        perf_file = self.log_dir / "performance.jsonl"
        with open(perf_file, "a") as f:
            f.write(json.dumps(perf_data) + "\n")

    def health_check(self) -> Dict[str, Any]:
        """Return system health status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "log_directory": str(self.log_dir),
            "log_files_count": len(list(self.log_dir.glob("*.log"))),
        }


# Global error tracker instance
error_tracker = ErrorTracker()


def track_errors(func):
    """Decorator to automatically track errors in functions"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_tracker.log_error(e, {"function": func.__name__, "args": str(args), "kwargs": str(kwargs)})
            raise

    return wrapper
