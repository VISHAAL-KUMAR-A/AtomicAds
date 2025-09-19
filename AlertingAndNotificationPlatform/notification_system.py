"""
Notification Delivery System with OOP Design Patterns
Implements Strategy, Factory, Observer, and State patterns
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import requests
import json


logger = logging.getLogger(__name__)


class DeliveryStatus(Enum):
    """
    State Pattern: Represents different delivery states
    """
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"


class NotificationChannel(ABC):
    """
    Strategy Pattern: Abstract base class for notification channels
    """

    @abstractmethod
    def send_notification(self, recipient: str, title: str, message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send notification through this channel

        Args:
            recipient: The recipient identifier (email, phone, user_id)
            title: Notification title
            message: Notification message
            metadata: Additional metadata for the notification

        Returns:
            Dict containing delivery status and details
        """
        pass

    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate if the recipient format is correct for this channel

        Args:
            recipient: The recipient identifier

        Returns:
            bool: True if valid, False otherwise
        """
        pass

    @abstractmethod
    def get_channel_name(self) -> str:
        """
        Get the name of this notification channel

        Returns:
            str: Channel name
        """
        pass


class EmailNotificationChannel(NotificationChannel):
    """
    Strategy Pattern Implementation: Email notification channel
    """

    def __init__(self):
        self.channel_name = "email"

    def send_notification(self, recipient: str, title: str, message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send email notification
        """
        try:
            if not self.validate_recipient(recipient):
                return {
                    'status': DeliveryStatus.FAILED.value,
                    'error': 'Invalid email address',
                    'channel': self.channel_name,
                    'timestamp': timezone.now()
                }

            # Enhanced email content with metadata
            email_body = self._format_email_body(title, message, metadata)

            send_mail(
                subject=f"Alert: {title}",
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )

            logger.info(f"Email sent successfully to {recipient}")
            return {
                'status': DeliveryStatus.SENT.value,
                'channel': self.channel_name,
                'recipient': recipient,
                'timestamp': timezone.now(),
                'message_id': f"email_{timezone.now().timestamp()}"
            }

        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return {
                'status': DeliveryStatus.FAILED.value,
                'error': str(e),
                'channel': self.channel_name,
                'recipient': recipient,
                'timestamp': timezone.now()
            }

    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate email address format
        """
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, recipient) is not None

    def get_channel_name(self) -> str:
        return self.channel_name

    def _format_email_body(self, title: str, message: str, metadata: Dict[str, Any] = None) -> str:
        """
        Format email body with metadata
        """
        body = f"""
{title}

{message}

---
This is an automated alert from the AtomicAds Notification System.
"""

        if metadata:
            body += f"\nAlert Details:\n"
            for key, value in metadata.items():
                body += f"- {key.replace('_', ' ').title()}: {value}\n"

        body += f"\nSent at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        return body


class SMSNotificationChannel(NotificationChannel):
    """
    Strategy Pattern Implementation: SMS notification channel
    """

    def __init__(self):
        self.channel_name = "sms"
        # Configure your SMS service (Twilio, AWS SNS, etc.)
        self.sms_api_url = getattr(settings, 'SMS_API_URL', None)
        self.sms_api_key = getattr(settings, 'SMS_API_KEY', None)

    def send_notification(self, recipient: str, title: str, message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send SMS notification
        """
        try:
            if not self.validate_recipient(recipient):
                return {
                    'status': DeliveryStatus.FAILED.value,
                    'error': 'Invalid phone number format',
                    'channel': self.channel_name,
                    'timestamp': timezone.now()
                }

            if not self.sms_api_url or not self.sms_api_key:
                logger.warning("SMS service not configured")
                return {
                    'status': DeliveryStatus.FAILED.value,
                    'error': 'SMS service not configured',
                    'channel': self.channel_name,
                    'timestamp': timezone.now()
                }

            # Format SMS message (shorter due to character limits)
            sms_message = self._format_sms_message(title, message, metadata)

            # Example SMS API call (adjust based on your SMS provider)
            response = self._send_sms_api(recipient, sms_message)

            if response.get('success'):
                logger.info(f"SMS sent successfully to {recipient}")
                return {
                    'status': DeliveryStatus.SENT.value,
                    'channel': self.channel_name,
                    'recipient': recipient,
                    'timestamp': timezone.now(),
                    'message_id': response.get('message_id', f"sms_{timezone.now().timestamp()}")
                }
            else:
                return {
                    'status': DeliveryStatus.FAILED.value,
                    'error': response.get('error', 'SMS send failed'),
                    'channel': self.channel_name,
                    'recipient': recipient,
                    'timestamp': timezone.now()
                }

        except Exception as e:
            logger.error(f"Failed to send SMS to {recipient}: {str(e)}")
            return {
                'status': DeliveryStatus.FAILED.value,
                'error': str(e),
                'channel': self.channel_name,
                'recipient': recipient,
                'timestamp': timezone.now()
            }

    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate phone number format
        """
        import re
        # Simple phone number validation (adjust based on your requirements)
        phone_pattern = r'^\+?1?-?\d{10,15}$'
        return re.match(phone_pattern, recipient.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) is not None

    def get_channel_name(self) -> str:
        return self.channel_name

    def _format_sms_message(self, title: str, message: str, metadata: Dict[str, Any] = None) -> str:
        """
        Format SMS message (keep it short)
        """
        severity = metadata.get('severity', '') if metadata else ''
        severity_prefix = f"[{severity.upper()}] " if severity else ""

        # Keep SMS under 160 characters when possible
        sms_text = f"{severity_prefix}{title}"
        if len(sms_text + message) < 140:
            sms_text += f": {message}"

        return sms_text

    def _send_sms_api(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Mock SMS API call - implement with your SMS provider
        """
        # This is a placeholder - implement with your actual SMS service
        # Examples: Twilio, AWS SNS, etc.

        # Mock successful response for demonstration
        return {
            'success': True,
            'message_id': f"sms_mock_{timezone.now().timestamp()}"
        }


class InAppNotificationChannel(NotificationChannel):
    """
    Strategy Pattern Implementation: In-app notification channel
    """

    def __init__(self):
        self.channel_name = "in_app"

    def send_notification(self, recipient: str, title: str, message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send in-app notification (store in database)
        """
        try:
            if not self.validate_recipient(recipient):
                return {
                    'status': DeliveryStatus.FAILED.value,
                    'error': 'Invalid user ID',
                    'channel': self.channel_name,
                    'timestamp': timezone.now()
                }

            # Store notification in database for in-app display
            notification_data = {
                'user_id': int(recipient),
                'title': title,
                'message': message,
                'metadata': metadata or {},
                'channel': self.channel_name,
                'created_at': timezone.now(),
                'is_read': False
            }

            # Here you would typically save to a notifications table
            # For now, we'll just log it
            logger.info(
                f"In-app notification created for user {recipient}: {title}")

            return {
                'status': DeliveryStatus.DELIVERED.value,
                'channel': self.channel_name,
                'recipient': recipient,
                'timestamp': timezone.now(),
                'notification_data': notification_data
            }

        except Exception as e:
            logger.error(
                f"Failed to create in-app notification for user {recipient}: {str(e)}")
            return {
                'status': DeliveryStatus.FAILED.value,
                'error': str(e),
                'channel': self.channel_name,
                'recipient': recipient,
                'timestamp': timezone.now()
            }

    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate user ID format
        """
        try:
            int(recipient)
            return True
        except ValueError:
            return False

    def get_channel_name(self) -> str:
        return self.channel_name


class NotificationChannelFactory:
    """
    Factory Pattern: Creates notification channels based on delivery type
    """

    _channels = {
        'email': EmailNotificationChannel,
        'sms': SMSNotificationChannel,
        'in_app': InAppNotificationChannel,
    }

    @classmethod
    def create_channel(cls, delivery_type: str) -> NotificationChannel:
        """
        Create a notification channel instance

        Args:
            delivery_type: Type of delivery channel ('email', 'sms', 'in_app')

        Returns:
            NotificationChannel: Instance of the requested channel

        Raises:
            ValueError: If delivery_type is not supported
        """
        if delivery_type not in cls._channels:
            raise ValueError(f"Unsupported delivery type: {delivery_type}")

        return cls._channels[delivery_type]()

    @classmethod
    def get_available_channels(cls) -> List[str]:
        """
        Get list of available notification channels

        Returns:
            List[str]: List of available channel names
        """
        return list(cls._channels.keys())

    @classmethod
    def register_channel(cls, delivery_type: str, channel_class: type):
        """
        Register a new notification channel

        Args:
            delivery_type: Name of the delivery type
            channel_class: Class implementing NotificationChannel interface
        """
        cls._channels[delivery_type] = channel_class


class NotificationObserver(ABC):
    """
    Observer Pattern: Abstract observer for notification events
    """

    @abstractmethod
    def on_notification_sent(self, notification_data: Dict[str, Any]):
        """Called when a notification is sent"""
        pass

    @abstractmethod
    def on_notification_failed(self, notification_data: Dict[str, Any]):
        """Called when a notification fails"""
        pass


class DeliveryTrackingObserver(NotificationObserver):
    """
    Observer Pattern Implementation: Tracks delivery statistics
    """

    def __init__(self):
        self.delivery_stats = {
            'sent': 0,
            'failed': 0,
            'by_channel': {}
        }

    def on_notification_sent(self, notification_data: Dict[str, Any]):
        """Track successful deliveries"""
        self.delivery_stats['sent'] += 1
        channel = notification_data.get('channel', 'unknown')
        if channel not in self.delivery_stats['by_channel']:
            self.delivery_stats['by_channel'][channel] = {
                'sent': 0, 'failed': 0}
        self.delivery_stats['by_channel'][channel]['sent'] += 1

        logger.info(
            f"Notification sent via {channel}: {notification_data.get('recipient')}")

    def on_notification_failed(self, notification_data: Dict[str, Any]):
        """Track failed deliveries"""
        self.delivery_stats['failed'] += 1
        channel = notification_data.get('channel', 'unknown')
        if channel not in self.delivery_stats['by_channel']:
            self.delivery_stats['by_channel'][channel] = {
                'sent': 0, 'failed': 0}
        self.delivery_stats['by_channel'][channel]['failed'] += 1

        logger.error(
            f"Notification failed via {channel}: {notification_data.get('error')}")

    def get_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        return self.delivery_stats.copy()


class NotificationService:
    """
    Main notification service that coordinates all patterns
    Implements Observer pattern for event notifications
    """

    def __init__(self):
        self.observers: List[NotificationObserver] = []
        self.factory = NotificationChannelFactory()
        self.retry_attempts = 3

        # Add default observer for tracking
        self.delivery_tracker = DeliveryTrackingObserver()
        self.add_observer(self.delivery_tracker)

    def add_observer(self, observer: NotificationObserver):
        """Add an observer for notification events"""
        self.observers.append(observer)

    def remove_observer(self, observer: NotificationObserver):
        """Remove an observer"""
        if observer in self.observers:
            self.observers.remove(observer)

    def _notify_observers_sent(self, notification_data: Dict[str, Any]):
        """Notify all observers of successful delivery"""
        for observer in self.observers:
            observer.on_notification_sent(notification_data)

    def _notify_observers_failed(self, notification_data: Dict[str, Any]):
        """Notify all observers of failed delivery"""
        for observer in self.observers:
            observer.on_notification_failed(notification_data)

    def send_notification(
        self,
        delivery_type: str,
        recipient: str,
        title: str,
        message: str,
        metadata: Dict[str, Any] = None,
        retry_on_failure: bool = True
    ) -> Dict[str, Any]:
        """
        Send a notification through the specified channel

        Args:
            delivery_type: Type of delivery ('email', 'sms', 'in_app')
            recipient: Recipient identifier
            title: Notification title
            message: Notification message
            metadata: Additional metadata
            retry_on_failure: Whether to retry on failure

        Returns:
            Dict: Delivery result
        """
        try:
            channel = self.factory.create_channel(delivery_type)

            for attempt in range(self.retry_attempts if retry_on_failure else 1):
                result = channel.send_notification(
                    recipient, title, message, metadata)

                if result['status'] in [DeliveryStatus.SENT.value, DeliveryStatus.DELIVERED.value]:
                    self._notify_observers_sent(result)
                    return result

                if attempt < self.retry_attempts - 1 and retry_on_failure:
                    logger.warning(
                        f"Retry attempt {attempt + 1} for {delivery_type} to {recipient}")
                    continue

                # Final failure
                self._notify_observers_failed(result)
                return result

        except Exception as e:
            error_result = {
                'status': DeliveryStatus.FAILED.value,
                'error': str(e),
                'channel': delivery_type,
                'recipient': recipient,
                'timestamp': timezone.now()
            }
            self._notify_observers_failed(error_result)
            return error_result

    def send_bulk_notification(
        self,
        notifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Send multiple notifications

        Args:
            notifications: List of notification data dicts

        Returns:
            List of delivery results
        """
        results = []
        for notification in notifications:
            result = self.send_notification(**notification)
            results.append(result)
        return results

    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        return self.delivery_tracker.get_stats()


# Singleton instance for global use
notification_service = NotificationService()
