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

    # Teams endpoint
    path('teams/', views.TeamListView.as_view(), name='teams'),

    # Alert endpoints
    path('alerts/', views.AlertListCreateView.as_view(), name='alerts'),
    path('alerts/<int:pk>/', views.AlertDetailView.as_view(), name='alert_detail'),
    path('alerts/stats/', views.alert_stats, name='alert_stats'),

    # User alert endpoints
    path('my-alerts/', views.UserAlertListView.as_view(), name='user_alerts'),
    path('alerts/<int:alert_id>/read/',
         views.MarkAlertAsReadView.as_view(), name='mark_alert_read'),
    path('alerts/<int:alert_id>/snooze/',
         views.SnoozeAlertView.as_view(), name='snooze_alert'),
    path('alerts/<int:alert_id>/unsnooze/',
         views.UnsnoozeAlertView.as_view(), name='unsnooze_alert'),
]
