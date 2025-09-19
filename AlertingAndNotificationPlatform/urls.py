from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'auth'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(),
         name='token_refresh'),

    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(),
         name='change_password'),
    path('dashboard/', views.user_dashboard, name='dashboard'),

    # Team management endpoints
    path('teams/', views.TeamListCreateView.as_view(), name='teams'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:team_id>/members/',
         views.TeamMemberManagementView.as_view(), name='team_members'),

    # Alert endpoints
    path('alerts/', views.AlertListCreateView.as_view(), name='alerts'),
    path('alerts/<int:pk>/', views.AlertDetailView.as_view(), name='alert_detail'),
    path('alerts/stats/', views.alert_stats, name='alert_stats'),
    path('alerts/<int:alert_id>/archive/',
         views.ArchiveAlertView.as_view(), name='archive_alert'),
    path('alerts/<int:alert_id>/tracking/',
         views.AlertTrackingView.as_view(), name='alert_tracking'),
    path('alerts/<int:alert_id>/toggle-reminder/',
         views.ToggleAlertReminderView.as_view(), name='toggle_alert_reminder'),

    # User alert endpoints
    path('my-alerts/', views.UserAlertListView.as_view(), name='user_alerts'),
    path('alerts/<int:alert_id>/read/',
         views.MarkAlertAsReadView.as_view(), name='mark_alert_read'),
    path('alerts/<int:alert_id>/snooze/',
         views.SnoozeAlertView.as_view(), name='snooze_alert'),
    path('alerts/<int:alert_id>/unsnooze/',
         views.UnsnoozeAlertView.as_view(), name='unsnooze_alert'),

    # Notification delivery endpoints
    path('alerts/<int:alert_id>/send-notification/',
         views.SendNotificationView.as_view(), name='send_notification'),
    path('alerts/<int:alert_id>/delivery-status/',
         views.NotificationDeliveryStatusView.as_view(), name='delivery_status'),
    path('alerts/<int:alert_id>/retry-notifications/',
         views.RetryFailedNotificationsView.as_view(), name='retry_notifications'),

    # Scheduler management endpoints
    path('scheduler/status/', views.SchedulerStatusView.as_view(),
         name='scheduler_status'),
    path('scheduler/control/', views.SchedulerControlView.as_view(),
         name='scheduler_control'),
    path('scheduler/run-task/', views.RunTaskView.as_view(), name='run_task'),
]
