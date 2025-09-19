from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class Team(models.Model):
    """
    Team model for organizing users into different departments/groups
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class User(AbstractUser):
    """
    Extended User model with team association and role management
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'End User'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='user')
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        ordering = ['email']


class Alert(models.Model):
    """
    Alert model for creating and managing organizational alerts
    """
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    DELIVERY_TYPE_CHOICES = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]

    VISIBILITY_CHOICES = [
        ('organization', 'Entire Organization'),
        ('teams', 'Specific Teams'),
        ('users', 'Specific Users'),
    ]

    title = models.CharField(max_length=200)
    message_body = models.TextField()
    severity = models.CharField(
        max_length=10, choices=SEVERITY_CHOICES, default='info')
    delivery_type = models.CharField(
        max_length=10, choices=DELIVERY_TYPE_CHOICES, default='in_app')
    reminder_frequency = models.IntegerField(
        default=2, help_text='Reminder frequency in hours')
    visibility_type = models.CharField(
        max_length=15, choices=VISIBILITY_CHOICES, default='organization')

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_alerts')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_severity_display()})"

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def get_target_users(self):
        """
        Get all users who should receive this alert based on visibility settings
        """
        if self.visibility_type == 'organization':
            return User.objects.filter(is_active=True)
        elif self.visibility_type == 'teams':
            team_ids = self.alert_recipients.filter(
                team__isnull=False).values_list('team_id', flat=True)
            return User.objects.filter(team_id__in=team_ids, is_active=True)
        elif self.visibility_type == 'users':
            user_ids = self.alert_recipients.filter(
                user__isnull=False).values_list('user_id', flat=True)
            return User.objects.filter(id__in=user_ids, is_active=True)
        return User.objects.none()

    class Meta:
        ordering = ['-created_at']


class AlertRecipient(models.Model):
    """
    Model to define specific recipients for alerts (teams or users)
    """
    alert = models.ForeignKey(
        Alert, on_delete=models.CASCADE, related_name='alert_recipients')
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.team:
            return f"Alert: {self.alert.title} -> Team: {self.team.name}"
        elif self.user:
            return f"Alert: {self.alert.title} -> User: {self.user.email}"
        return f"Alert: {self.alert.title} -> Unknown Recipient"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(team__isnull=False) | models.Q(
                    user__isnull=False),
                name='alert_recipient_must_have_team_or_user'
            ),
            models.UniqueConstraint(
                fields=['alert', 'team'],
                condition=models.Q(team__isnull=False),
                name='unique_alert_team'
            ),
            models.UniqueConstraint(
                fields=['alert', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_alert_user'
            ),
        ]


class AlertStatus(models.Model):
    """
    Model to track individual user's interaction with alerts
    """
    alert = models.ForeignKey(
        Alert, on_delete=models.CASCADE, related_name='alert_statuses')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='alert_statuses')

    is_read = models.BooleanField(default=False)
    is_snoozed = models.BooleanField(default=False)
    snoozed_until = models.DateTimeField(null=True, blank=True)
    last_reminded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.alert.title} ({'Read' if self.is_read else 'Unread'})"

    @property
    def is_snoozed_active(self):
        """Check if alert is currently snoozed"""
        if self.is_snoozed and self.snoozed_until:
            return timezone.now() < self.snoozed_until
        return False

    def should_remind(self):
        """Check if user should receive a reminder for this alert"""
        if self.is_read or self.is_snoozed_active or self.alert.is_expired:
            return False

        if not self.last_reminded_at:
            return True

        time_since_last_reminder = timezone.now() - self.last_reminded_at
        reminder_interval = timedelta(hours=self.alert.reminder_frequency)
        return time_since_last_reminder >= reminder_interval

    class Meta:
        unique_together = ['alert', 'user']
        ordering = ['-created_at']
