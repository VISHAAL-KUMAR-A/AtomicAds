"""
Management command to reset expired snoozes
This command should be run daily (e.g., at midnight) via cron job
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from AlertingAndNotificationPlatform.models import AlertStatus
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reset expired snoozes for alert statuses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be reset without actually resetting snoozes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting snooze reset process (dry_run={dry_run})"
            )
        )

        # Find all alert statuses with expired snoozes
        now = timezone.now()
        expired_snoozes = AlertStatus.objects.filter(
            is_snoozed=True,
            snoozed_until__lt=now
        ).select_related('user', 'alert')

        total_count = expired_snoozes.count()

        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS("No expired snoozes found")
            )
            return

        self.stdout.write(f"Found {total_count} expired snoozes to reset")

        if dry_run:
            # Show what would be reset
            for alert_status in expired_snoozes[:10]:  # Show first 10
                self.stdout.write(
                    f"  [DRY RUN] Would reset snooze for: {alert_status.user.email} "
                    f"on alert '{alert_status.alert.title}' "
                    f"(expired: {alert_status.snoozed_until})"
                )

            if total_count > 10:
                self.stdout.write(f"  ... and {total_count - 10} more")

            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Would reset {total_count} expired snoozes"
                )
            )
        else:
            # Actually reset the snoozes
            updated_count = expired_snoozes.update(
                is_snoozed=False,
                snoozed_until=None
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully reset {updated_count} expired snoozes"
                )
            )

            logger.info(f"Reset {updated_count} expired snoozes")

        # Also provide statistics about current snooze status
        total_snoozed = AlertStatus.objects.filter(is_snoozed=True).count()
        active_snoozes = AlertStatus.objects.filter(
            is_snoozed=True,
            snoozed_until__gt=now
        ).count()

        self.stdout.write(
            f"\nSnooze statistics after processing:"
        )
        self.stdout.write(f"  Total snoozed alerts: {total_snoozed}")
        self.stdout.write(f"  Active snoozes: {active_snoozes}")

        if not dry_run:
            expired_after_reset = AlertStatus.objects.filter(
                is_snoozed=True,
                snoozed_until__lt=now
            ).count()
            self.stdout.write(
                f"  Expired snoozes remaining: {expired_after_reset}")
