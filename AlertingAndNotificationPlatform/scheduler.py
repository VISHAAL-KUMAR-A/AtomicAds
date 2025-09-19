"""
Scheduler service for background tasks
Provides utilities for scheduling and managing recurring tasks
"""

import os
import logging
from django.core.management import call_command
from django.conf import settings
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import time

logger = logging.getLogger(__name__)


class TaskResult:
    """
    Represents the result of a scheduled task execution
    """

    def __init__(self, task_name: str, success: bool, message: str = "", duration: float = 0.0):
        self.task_name = task_name
        self.success = success
        self.message = message
        self.duration = duration
        self.timestamp = datetime.now()

    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"[{self.timestamp}] {self.task_name}: {status} ({self.duration:.2f}s) - {self.message}"


class ScheduledTask:
    """
    Represents a scheduled task with its configuration
    """

    def __init__(
        self,
        name: str,
        command: str,
        interval_minutes: int,
        args: List[str] = None,
        enabled: bool = True,
        max_retries: int = 3
    ):
        self.name = name
        self.command = command
        self.interval_minutes = interval_minutes
        self.args = args or []
        self.enabled = enabled
        self.max_retries = max_retries
        self.last_run = None
        self.next_run = None
        self.execution_count = 0
        self.failure_count = 0
        self.last_result = None

    def is_due(self) -> bool:
        """Check if the task is due to run"""
        if not self.enabled:
            return False

        if self.next_run is None:
            return True

        return datetime.now() >= self.next_run

    def update_next_run(self):
        """Update the next run time based on interval"""
        self.next_run = datetime.now() + timedelta(minutes=self.interval_minutes)

    def execute(self) -> TaskResult:
        """Execute the scheduled task"""
        start_time = time.time()

        try:
            logger.info(f"Executing scheduled task: {self.name}")

            # Execute the Django management command
            call_command(self.command, *self.args)

            duration = time.time() - start_time
            self.execution_count += 1
            self.last_run = datetime.now()
            self.update_next_run()

            result = TaskResult(
                self.name, True, "Task completed successfully", duration)
            self.last_result = result

            logger.info(
                f"Task {self.name} completed successfully in {duration:.2f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time
            self.failure_count += 1
            error_message = str(e)

            result = TaskResult(self.name, False, error_message, duration)
            self.last_result = result

            logger.error(
                f"Task {self.name} failed after {duration:.2f}s: {error_message}")
            return result

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the task"""
        return {
            'name': self.name,
            'command': self.command,
            'interval_minutes': self.interval_minutes,
            'enabled': self.enabled,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'execution_count': self.execution_count,
            'failure_count': self.failure_count,
            'last_result': {
                'success': self.last_result.success,
                'message': self.last_result.message,
                'duration': self.last_result.duration,
                'timestamp': self.last_result.timestamp.isoformat()
            } if self.last_result else None
        }


class TaskScheduler:
    """
    Simple task scheduler for managing recurring background tasks
    """

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_thread = None
        self.execution_history: List[TaskResult] = []
        self.max_history_size = 1000

        # Register default tasks
        self._register_default_tasks()

    def _register_default_tasks(self):
        """Register the default system tasks"""

        # Send reminders every 30 minutes
        self.register_task(
            name="send_reminders",
            command="send_reminders",
            interval_minutes=30,
            args=["--max-reminders", "50"]
        )

        # Reset expired snoozes daily at 1 AM
        # Note: In production, this should be handled by cron at a specific time
        self.register_task(
            name="reset_daily_snoozes",
            command="reset_daily_snoozes",
            interval_minutes=1440,  # 24 hours
            enabled=True
        )

    def register_task(
        self,
        name: str,
        command: str,
        interval_minutes: int,
        args: List[str] = None,
        enabled: bool = True,
        max_retries: int = 3
    ):
        """Register a new scheduled task"""
        task = ScheduledTask(name, command, interval_minutes,
                             args, enabled, max_retries)
        self.tasks[name] = task
        logger.info(
            f"Registered task: {name} (interval: {interval_minutes} minutes)")

    def unregister_task(self, name: str):
        """Unregister a scheduled task"""
        if name in self.tasks:
            del self.tasks[name]
            logger.info(f"Unregistered task: {name}")

    def enable_task(self, name: str):
        """Enable a scheduled task"""
        if name in self.tasks:
            self.tasks[name].enabled = True
            logger.info(f"Enabled task: {name}")

    def disable_task(self, name: str):
        """Disable a scheduled task"""
        if name in self.tasks:
            self.tasks[name].enabled = False
            logger.info(f"Disabled task: {name}")

    def run_task_now(self, name: str) -> Optional[TaskResult]:
        """Run a specific task immediately"""
        if name not in self.tasks:
            logger.error(f"Task not found: {name}")
            return None

        task = self.tasks[name]
        result = task.execute()
        self._add_to_history(result)
        return result

    def _add_to_history(self, result: TaskResult):
        """Add a task result to execution history"""
        self.execution_history.append(result)

        # Keep history size manageable
        if len(self.execution_history) > self.max_history_size:
            self.execution_history = self.execution_history[-self.max_history_size:]

    def _scheduler_loop(self):
        """Main scheduler loop that runs in a separate thread"""
        logger.info("Task scheduler started")

        while self.running:
            try:
                # Check each task to see if it's due
                for task in self.tasks.values():
                    if task.is_due():
                        result = task.execute()
                        self._add_to_history(result)

                # Sleep for 1 minute before checking again
                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue after error

        logger.info("Task scheduler stopped")

    def start(self):
        """Start the task scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Task scheduler has been started")

    def stop(self):
        """Stop the task scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return

        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        logger.info("Task scheduler has been stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the scheduler and all tasks"""
        return {
            'running': self.running,
            'total_tasks': len(self.tasks),
            'enabled_tasks': len([t for t in self.tasks.values() if t.enabled]),
            'tasks': {name: task.get_status() for name, task in self.tasks.items()},
            'recent_executions': [
                {
                    'task_name': result.task_name,
                    'success': result.success,
                    'message': result.message,
                    'duration': result.duration,
                    'timestamp': result.timestamp.isoformat()
                }
                # Last 10 executions
                for result in self.execution_history[-10:]
            ]
        }

    def get_cron_setup_guide(self) -> str:
        """Generate a cron setup guide for production deployment"""
        guide = """
# AtomicAds Notification System - Cron Job Setup Guide

# Add these lines to your crontab (run 'crontab -e' to edit):

# Send reminder notifications every 30 minutes
*/30 * * * * cd /path/to/your/project && python manage.py send_reminders --max-reminders 100

# Reset expired snoozes daily at 1:00 AM
0 1 * * * cd /path/to/your/project && python manage.py reset_daily_snoozes

# Optional: Clean up old notification delivery logs weekly (Sunday at 2:00 AM)
0 2 * * 0 cd /path/to/your/project && python manage.py shell -c "from AlertingAndNotificationPlatform.models import NotificationDelivery; from django.utils import timezone; from datetime import timedelta; NotificationDelivery.objects.filter(created_at__lt=timezone.now() - timedelta(days=30)).delete()"

# For debugging, you can run commands manually:
# python manage.py send_reminders --dry-run
# python manage.py reset_daily_snoozes --dry-run

# Production considerations:
# 1. Replace '/path/to/your/project' with your actual project path
# 2. Use virtual environment: '/path/to/venv/bin/python manage.py ...'
# 3. Add logging: '>> /var/log/atomicads/cron.log 2>&1'
# 4. Consider using a process manager like supervisord for more complex scheduling
# 5. Monitor cron job execution and set up alerts for failures
"""
        return guide


# Global scheduler instance
scheduler = TaskScheduler()


# Django app ready hook to start scheduler in production
def start_scheduler_if_enabled():
    """
    Start the scheduler if enabled in settings
    This should be called from the app's ready() method
    """
    if getattr(settings, 'ENABLE_TASK_SCHEDULER', False):
        scheduler.start()
        logger.info("Task scheduler started automatically")
    else:
        logger.info(
            "Task scheduler is disabled (set ENABLE_TASK_SCHEDULER=True to enable)")
