"""
Management command to send alert reminders
This command should be run periodically (e.g., every 30 minutes) via cron job or task scheduler
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from AlertingAndNotificationPlatform.models import Alert, AlertStatus, NotificationDelivery
from AlertingAndNotificationPlatform.notification_system import notification_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send reminders for active alerts to users who need them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending reminders',
        )
        parser.add_argument(
            '--alert-id',
            type=int,
            help='Send reminders only for a specific alert ID',
        )
        parser.add_argument(
            '--max-reminders',
            type=int,
            default=100,
            help='Maximum number of reminders to send in this run (default: 100)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        alert_id = options['alert_id']
        max_reminders = options['max_reminders']

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting reminder sending process (dry_run={dry_run})"
            )
        )

        # Get alerts that are active and have reminders enabled
        alerts_query = Alert.objects.filter(
            is_active=True,
            is_archived=False,
            reminder_enabled=True
        )

        if alert_id:
            alerts_query = alerts_query.filter(id=alert_id)

        # Only include alerts that are currently active (started and not expired)
        active_alerts = []
        for alert in alerts_query:
            if alert.is_currently_active:
                active_alerts.append(alert)

        if not active_alerts:
            self.stdout.write(
                self.style.WARNING(
                    "No active alerts with reminders enabled found")
            )
            return

        self.stdout.write(
            f"Found {len(active_alerts)} active alerts with reminders enabled")

        total_reminders_sent = 0
        total_recipients_processed = 0
        reminder_results = []

        for alert in active_alerts:
            if total_reminders_sent >= max_reminders:
                self.stdout.write(
                    self.style.WARNING(
                        f"Reached maximum reminder limit ({max_reminders}), stopping"
                    )
                )
                break

            self.stdout.write(
                f"\nProcessing alert: {alert.title} (ID: {alert.id})")

            # Get all alert statuses for this alert that need reminders
            alert_statuses = AlertStatus.objects.filter(alert=alert)

            reminder_count_for_alert = 0
            for alert_status in alert_statuses:
                if total_reminders_sent >= max_reminders:
                    break

                if alert_status.should_remind():
                    total_recipients_processed += 1

                    if dry_run:
                        self.stdout.write(
                            f"  [DRY RUN] Would send reminder to: {alert_status.user.email}"
                        )
                        reminder_results.append({
                            'alert_id': alert.id,
                            'user_email': alert_status.user.email,
                            'action': 'would_send',
                            'dry_run': True
                        })
                        continue

                    # Send the reminder
                    reminder_result = self._send_reminder(alert, alert_status)
                    reminder_results.append(reminder_result)

                    if reminder_result['status'] == 'sent':
                        total_reminders_sent += 1
                        reminder_count_for_alert += 1

                        # Update the last_reminded_at timestamp
                        alert_status.last_reminded_at = timezone.now()
                        alert_status.save(update_fields=['last_reminded_at'])

            if not dry_run:
                self.stdout.write(
                    f"  Sent {reminder_count_for_alert} reminders for this alert"
                )

        # Print summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nReminder sending completed:"
            )
        )
        self.stdout.write(
            f"  Total recipients processed: {total_recipients_processed}")
        self.stdout.write(f"  Total reminders sent: {total_reminders_sent}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "  (This was a dry run - no actual reminders were sent)")
            )

        # Show failed reminders if any
        failed_reminders = [
            r for r in reminder_results if r['status'] == 'failed']
        if failed_reminders:
            self.stdout.write(
                self.style.ERROR(
                    f"\nFailed reminders: {len(failed_reminders)}")
            )
            for failed in failed_reminders[:5]:  # Show first 5 failures
                self.stdout.write(
                    f"  - {failed['user_email']}: {failed['error']}")

    def _send_reminder(self, alert, alert_status):
        """
        Send a reminder for a specific alert to a specific user
        """
        user = alert_status.user

        try:
            # Determine recipient based on delivery type
            if alert.delivery_type == 'email':
                recipient = user.email
            elif alert.delivery_type == 'sms':
                recipient = user.phone_number
                if not recipient:
                    return {
                        'alert_id': alert.id,
                        'user_email': user.email,
                        'status': 'failed',
                        'error': 'No phone number available'
                    }
            else:  # in_app
                recipient = str(user.id)

            # Prepare reminder metadata
            reminder_count = (alert_status.last_reminded_at is not None)
            metadata = {
                'alert_id': alert.id,
                'severity': alert.severity,
                'visibility_type': alert.visibility_type,
                'is_reminder': True,
                'reminder_count': reminder_count,
                'reminder_frequency_hours': alert.reminder_frequency
            }

            # Format reminder title
            reminder_title = f"REMINDER: {alert.title}"

            # Send the reminder notification
            result = notification_service.send_notification(
                delivery_type=alert.delivery_type,
                recipient=recipient,
                title=reminder_title,
                message=alert.message_body,
                metadata=metadata
            )

            # Create delivery log for the reminder
            NotificationDelivery.objects.create(
                alert=alert,
                user=user,
                delivery_type=alert.delivery_type,
                recipient=recipient,
                status=result['status'],
                message_id=result.get('message_id'),
                error_message=result.get('error'),
                attempt_count=1,
                last_attempt_at=timezone.now(),
                delivered_at=timezone.now() if result['status'] in [
                    'sent', 'delivered'] else None,
                metadata=metadata
            )

            return {
                'alert_id': alert.id,
                'user_email': user.email,
                'status': result['status'],
                'channel': result['channel'],
                'recipient': recipient,
                'error': result.get('error')
            }

        except Exception as e:
            logger.error(
                f"Failed to send reminder for alert {alert.id} to user {user.email}: {str(e)}")
            return {
                'alert_id': alert.id,
                'user_email': user.email,
                'status': 'failed',
                'error': str(e)
            }
