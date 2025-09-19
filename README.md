# 🚀 AtomicAds - Complete Alerting & Notification Platform

A comprehensive Django REST API based alerting and notification platform with JWT authentication, team management, notification delivery system, and background task scheduling.

## 📋 Table of Contents

1. [Quick Setup](#quick-setup)
2. [Test Accounts](#test-accounts)
3. [Authentication APIs](#authentication-apis)
4. [Alert Management APIs](#alert-management-apis)
5. [Team Management APIs](#team-management-apis)
6. [Notification Delivery APIs](#notification-delivery-apis)
7. [Scheduler Management APIs](#scheduler-management-apis)
8. [Enhanced Alert Features](#enhanced-alert-features)
9. [Testing Guide](#testing-guide)
10. [Project Structure](#project-structure)
11. [Features Implemented](#features-implemented)
12. [Troubleshooting](#troubleshooting)

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Seed Data
```bash
python manage.py create_seed_data
```

### 4. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 5. Run the Server
```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

**Base URLs:**
- Authentication: `http://127.0.0.1:8000/api/auth/`
- Alerts: `http://127.0.0.1:8000/api/alerts/`
- Teams: `http://127.0.0.1:8000/api/teams/`
- Scheduler: `http://127.0.0.1:8000/api/scheduler/`

## 👥 Test Accounts

After running the seed data command, you can use these test accounts:

### Admin Users:
- **Email:** `admin@atomicads.com` | **Password:** `admin123456`
- **Email:** `alice.brown@atomicads.com` | **Password:** `user123456`

### Regular Users:
- **Email:** `john.doe@atomicads.com` | **Password:** `user123456`
- **Email:** `jane.smith@atomicads.com` | **Password:** `user123456`
- **Email:** `bob.wilson@atomicads.com` | **Password:** `user123456`

---

## 🔐 Authentication APIs

### Base URL: `/api/auth/`

### 1. User Registration
**Endpoint:** `POST /api/auth/register/`  
**Authentication:** None required

**Request Body:**
```json
{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword123",
    "confirm_password": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "role": "user",
    "team_name": "Engineering",
    "phone_number": "+1234567890"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 6,
        "username": "testuser",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "team": "Engineering"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 2. User Login
**Endpoint:** `POST /api/auth/login/`  
**Authentication:** None required

**Request Body:**
```json
{
    "email": "admin@atomicads.com",
    "password": "admin123456"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "admin_user",
        "email": "admin@atomicads.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "team": "Engineering"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 3. Token Refresh
**Endpoint:** `POST /api/auth/token/refresh/`  
**Authentication:** None required

**Request Body:**
```json
{
    "refresh": "your_refresh_token_here"
}
```

**Response (200 OK):**
```json
{
    "access": "new_access_token_here"
}
```

### 4. User Logout
**Endpoint:** `POST /api/auth/logout/`  
**Authentication:** Bearer Token required

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
    "refresh": "your_refresh_token_here"
}
```

**Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

### 5. User Profile
**Endpoint:** `GET /api/auth/profile/`  
**Authentication:** Bearer Token required

**Response:**
```json
{
    "id": 1,
    "username": "admin_user",
    "email": "admin@atomicads.com",
    "first_name": "Admin",
    "last_name": "User",
    "full_name": "Admin User",
    "role": "admin",
    "team": {
        "id": 1,
        "name": "Engineering",
        "description": "Software development and technical operations team",
        "created_at": "2025-01-01T00:00:00Z"
    },
    "phone_number": null,
    "is_active": true,
    "date_joined": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-01T00:00:00Z"
}
```

### 6. Update User Profile
**Endpoint:** `PATCH /api/auth/profile/`  
**Authentication:** Bearer Token required

**Request Body:**
```json
{
    "first_name": "Updated First Name",
    "last_name": "Updated Last Name",
    "phone_number": "+9876543210"
}
```

### 7. Change Password
**Endpoint:** `POST /api/auth/change-password/`  
**Authentication:** Bearer Token required

**Request Body:**
```json
{
    "old_password": "current_password",
    "new_password": "new_secure_password123",
    "confirm_new_password": "new_secure_password123"
}
```

**Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

### 8. User Dashboard
**Endpoint:** `GET /api/auth/dashboard/`  
**Authentication:** Bearer Token required

**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "admin_user",
        "email": "admin@atomicads.com",
        "full_name": "Admin User",
        "role": "admin",
        "team": "Engineering",
        "is_admin": true
    },
    "stats": {
        "total_users": 5,
        "total_teams": 4
    }
}
```

### 9. List Teams
**Endpoint:** `GET /api/auth/teams/`  
**Authentication:** Bearer Token required

---

## 🚨 Alert Management APIs

### Base URL: `/api/alerts/`

### 1. Create Alert (Admin Only)
**Endpoint:** `POST /api/alerts/`  
**Authentication:** Bearer Token required (Admin)

**Request Body:**
```json
{
    "title": "System Maintenance Alert",
    "message_body": "Scheduled system maintenance will occur on Friday evening.",
    "severity": "warning",
    "delivery_type": "email",
    "reminder_frequency": 4,
    "reminder_enabled": true,
    "visibility_type": "organization",
    "starts_at": "2024-01-15T18:00:00Z",
    "expires_at": "2024-01-16T06:00:00Z",
    "recipient_teams": [1, 2],
    "recipient_users": [3, 4]
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "title": "System Maintenance Alert",
    "message_body": "Scheduled system maintenance will occur on Friday evening.",
    "severity": "warning",
    "delivery_type": "email",
    "reminder_frequency": 4,
    "reminder_enabled": true,
    "visibility_type": "organization",
    "is_active": true,
    "is_archived": false,
    "starts_at": "2024-01-15T18:00:00Z",
    "expires_at": "2024-01-16T06:00:00Z",
    "created_by": 1,
    "created_by_name": "Admin User",
    "recipients": [],
    "is_expired": false,
    "is_started": true,
    "is_currently_active": true,
    "status": "active",
    "created_at": "2025-09-19T12:00:00Z",
    "updated_at": "2025-09-19T12:00:00Z"
}
```

### 2. List Alerts with Enhanced Filtering
**Endpoint:** `GET /api/alerts/`  
**Authentication:** Bearer Token required

**Query Parameters:**
- `status`: `active`, `expired`, `scheduled`, `archived`, `inactive`
- `severity`: `info`, `warning`, `critical`
- `audience`: `organization`, `teams`, `users`
- `created_by`: User ID
- `start_date`: ISO datetime
- `end_date`: ISO datetime

**Examples:**
- Filter active alerts: `/api/alerts/?status=active`
- Filter by severity: `/api/alerts/?severity=critical&status=active`
- Filter by date range: `/api/alerts/?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z`

### 3. Get Alert Details
**Endpoint:** `GET /api/alerts/{alert_id}/`  
**Authentication:** Bearer Token required

### 4. Update Alert (Admin Only)
**Endpoint:** `PATCH /api/alerts/{alert_id}/`  
**Authentication:** Bearer Token required (Admin)

**Request Body:**
```json
{
    "title": "Updated: System Maintenance Alert",
    "message_body": "The maintenance window has been moved to 3:00 AM to 5:00 AM UTC."
}
```

### 5. Delete Alert (Admin Only)
**Endpoint:** `DELETE /api/alerts/{alert_id}/`  
**Authentication:** Bearer Token required (Admin)

### 6. Archive/Unarchive Alert (Admin Only)
**Endpoint:** `POST /api/alerts/{alert_id}/archive/`  
**Authentication:** Bearer Token required (Admin)

**Request Body:**
```json
{
    "is_archived": true
}
```

**Response:**
```json
{
    "message": "Alert archived successfully",
    "alert_id": 123,
    "is_archived": true
}
```

### 7. Toggle Alert Reminders (Admin Only)
**Endpoint:** `POST /api/alerts/{alert_id}/toggle-reminder/`  
**Authentication:** Bearer Token required (Admin)

**Response:**
```json
{
    "message": "Alert reminders enabled successfully",
    "alert_id": 123,
    "reminder_enabled": true
}
```

### 8. View My Alerts (User)
**Endpoint:** `GET /api/alerts/my-alerts/`  
**Authentication:** Bearer Token required

**Query Parameters:**
- `read`: `true`/`false` - Filter by read status
- `severity`: `info`, `warning`, `critical`

**Response:**
```json
{
    "summary": {
        "total_alerts": 3,
        "unread_alerts": 2,
        "snoozed_alerts": 1
    },
    "alerts": [
        {
            "id": 1,
            "title": "System Maintenance Alert",
            "message_body": "The system will be under maintenance...",
            "severity": "warning",
            "delivery_type": "email",
            "reminder_frequency": 2,
            "created_by_name": "Admin User",
            "is_expired": false,
            "created_at": "2025-09-19T12:00:00Z",
            "alert_status": {
                "is_read": false,
                "is_snoozed": false,
                "snoozed_until": null,
                "is_snoozed_active": false
            }
        }
    ]
}
```

### 9. Mark Alert as Read (User)
**Endpoint:** `POST /api/alerts/{alert_id}/read/`  
**Authentication:** Bearer Token required

### 10. Snooze Alert (User)
**Endpoint:** `POST /api/alerts/{alert_id}/snooze/`  
**Authentication:** Bearer Token required

**Request Body:**
```json
{
    "hours": 4
}
```

### 11. Unsnooze Alert (User)
**Endpoint:** `POST /api/alerts/{alert_id}/unsnooze/`  
**Authentication:** Bearer Token required

### 12. Alert Statistics (Admin Only)
**Endpoint:** `GET /api/alerts/stats/`  
**Authentication:** Bearer Token required (Admin)

**Response:**
```json
{
    "alert_stats": {
        "total_alerts": 25,
        "active_alerts": 15,
        "expired_alerts": 3,
        "archived_alerts": 5,
        "scheduled_alerts": 2,
        "recent_alerts": 8
    },
    "reminder_stats": {
        "reminders_enabled": 20,
        "reminders_disabled": 5
    },
    "severity_breakdown": {
        "info": 10,
        "warning": 12,
        "critical": 3
    },
    "interaction_stats": {
        "total_recipients": 500,
        "read_count": 350,
        "unread_count": 150,
        "snoozed_count": 45,
        "read_percentage": 70.0
    }
}
```

### 13. Alert Tracking (Admin Only)
**Endpoint:** `GET /api/alerts/{alert_id}/tracking/`  
**Authentication:** Bearer Token required (Admin)

**Response:**
```json
{
    "alert_id": 123,
    "alert_title": "System Maintenance Alert",
    "alert_status": "active",
    "total_recipients": 50,
    "interaction_stats": {
        "read_count": 35,
        "unread_count": 15,
        "read_percentage": 70.0
    },
    "snooze_stats": {
        "currently_snoozed": 8,
        "total_ever_snoozed": 12,
        "snoozed_percentage": 16.0,
        "most_users_snoozed": false
    },
    "is_recurring": true
}
```

---

## 🏢 Team Management APIs

### Base URL: `/api/teams/`

### 1. List All Teams
**Endpoint:** `GET /api/teams/`  
**Authentication:** Bearer Token required

**Response:**
```json
[
    {
        "id": 1,
        "name": "Engineering",
        "description": "Software development team",
        "member_count": 5,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
]
```

### 2. Create New Team (Admin Only)
**Endpoint:** `POST /api/teams/`  
**Authentication:** Bearer Token required (Admin)

**Request Body:**
```json
{
    "name": "Marketing Team",
    "description": "Marketing and communications team"
}
```

**Response (201 Created):**
```json
{
    "id": 3,
    "name": "Marketing Team",
    "description": "Marketing and communications team",
    "member_count": 0,
    "created_at": "2024-01-20T14:25:00Z",
    "updated_at": "2024-01-20T14:25:00Z"
}
```

### 3. Get Team Details
**Endpoint:** `GET /api/teams/{team_id}/`  
**Authentication:** Bearer Token required

**Response:**
```json
{
    "id": 1,
    "name": "Engineering",
    "description": "Software development team",
    "member_count": 3,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "members": [
        {
            "id": 2,
            "email": "john.doe@company.com",
            "full_name": "John Doe",
            "role": "user",
            "is_active": true
        }
    ]
}
```

### 4. Update Team (Admin Only)
**Endpoint:** `PUT /api/teams/{team_id}/`  
**Authentication:** Bearer Token required (Admin)

**Request Body:**
```json
{
    "name": "Senior Engineering Team",
    "description": "Senior software development and architecture team"
}
```

### 5. Delete Team (Admin Only)
**Endpoint:** `DELETE /api/teams/{team_id}/`  
**Authentication:** Bearer Token required (Admin)

**Response:**
```json
{
    "message": "Team deleted successfully"
}
```

### 6. Manage Team Members (Admin Only)

#### Assign Users to Team:
**Endpoint:** `POST /api/teams/{team_id}/members/`  
**Authentication:** Bearer Token required (Admin)

**Request Body:**
```json
{
    "user_ids": [2, 3, 4],
    "action": "assign"
}
```

**Response:**
```json
{
    "message": "Successfully assigned 3 users to team Engineering",
    "team_id": 1,
    "team_name": "Engineering",
    "action": "assign",
    "affected_users": 3
}
```

#### Remove Users from Team:
**Request Body:**
```json
{
    "user_ids": [2, 3],
    "action": "remove"
}
```

**Response:**
```json
{
    "message": "Successfully removed 2 users from team Engineering",
    "team_id": 1,
    "team_name": "Engineering",
    "action": "remove",
    "affected_users": 2
}
```

#### Get Team Members:
**Endpoint:** `GET /api/teams/{team_id}/members/`  
**Authentication:** Bearer Token required (Admin)

---

## 📬 Notification Delivery APIs

### Base URL: `/api/alerts/`

### 1. Send Manual Notification (Admin Only)
**Endpoint:** `POST /api/alerts/{alert_id}/send-notification/`  
**Authentication:** Bearer Token required (Admin)

**Response:**
```json
{
    "message": "Notification sending completed for alert: Critical System Update",
    "alert_id": 1,
    "total_recipients": 5,
    "delivery_results": [
        {
            "user_id": 2,
            "user_email": "john.doe@company.com",
            "delivery_id": 15,
            "status": "sent",
            "channel": "email",
            "recipient": "john.doe@company.com",
            "error": null
        },
        {
            "user_id": 3,
            "user_email": "jane.smith@company.com",
            "delivery_id": 16,
            "status": "failed",
            "channel": "sms",
            "recipient": "+1234567890",
            "error": "SMS service not configured"
        }
    ],
    "delivery_stats": {
        "sent": 3,
        "failed": 2,
        "by_channel": {
            "email": {"sent": 3, "failed": 0},
            "sms": {"sent": 0, "failed": 2}
        }
    }
}
```

### 2. Check Delivery Status (Admin Only)
**Endpoint:** `GET /api/alerts/{alert_id}/delivery-status/`  
**Authentication:** Bearer Token required (Admin)

**Response:**
```json
{
    "alert_id": 1,
    "alert_title": "Critical System Update",
    "delivery_summary": {
        "total_deliveries": 5,
        "sent_count": 3,
        "failed_count": 2,
        "pending_count": 0,
        "success_rate": 60.0
    },
    "delivery_logs": [
        {
            "id": 15,
            "user": {
                "id": 2,
                "email": "john.doe@company.com",
                "full_name": "John Doe"
            },
            "delivery_type": "email",
            "recipient": "john.doe@company.com",
            "status": "sent",
            "message_id": "email_1642686000.123",
            "error_message": null,
            "attempt_count": 1,
            "last_attempt_at": "2024-01-20T15:00:00Z",
            "delivered_at": "2024-01-20T15:00:00Z",
            "created_at": "2024-01-20T15:00:00Z"
        }
    ]
}
```

### 3. Retry Failed Notifications (Admin Only)
**Endpoint:** `POST /api/alerts/{alert_id}/retry-notifications/`  
**Authentication:** Bearer Token required (Admin)

**Response:**
```json
{
    "message": "Retry completed for 2 failed notifications",
    "alert_id": 1,
    "retry_results": [
        {
            "delivery_id": 16,
            "user_email": "jane.smith@company.com",
            "status": "sent",
            "attempt_count": 2,
            "error": null
        }
    ]
}
```

---

## ⏰ Scheduler Management APIs

### Base URL: `/api/scheduler/`

### 1. Get Scheduler Status (Admin Only)
**Endpoint:** `GET /api/scheduler/status/`  
**Authentication:** Bearer Token required (Admin)

**Response:**
```json
{
    "scheduler_status": {
        "running": true,
        "total_tasks": 2,
        "enabled_tasks": 2,
        "tasks": {
            "send_reminders": {
                "name": "send_reminders",
                "command": "send_reminders",
                "interval_minutes": 30,
                "enabled": true,
                "last_run": "2024-01-20T15:30:00Z",
                "next_run": "2024-01-20T16:00:00Z",
                "execution_count": 48,
                "failure_count": 2,
                "last_result": {
                    "success": true,
                    "message": "Task completed successfully",
                    "duration": 2.35,
                    "timestamp": "2024-01-20T15:30:00Z"
                }
            }
        },
        "recent_executions": []
    },
    "cron_setup_guide": "# AtomicAds Notification System - Cron Job Setup Guide..."
}
```

### 2. Control Scheduler (Admin Only)

#### Start Scheduler:
**Endpoint:** `POST /api/scheduler/control/`  
**Authentication:** Bearer Token required (Admin)

**Request Body:**
```json
{
    "action": "start"
}
```

**Response:**
```json
{
    "message": "Scheduler started successfully",
    "action": "start",
    "scheduler_running": true
}
```

#### Stop Scheduler:
**Request Body:**
```json
{
    "action": "stop"
}
```

**Response:**
```json
{
    "message": "Scheduler stopped successfully",
    "action": "stop",
    "scheduler_running": false
}
```

### 3. Run Task Manually (Admin Only)
**Endpoint:** `POST /api/scheduler/run-task/`  
**Authentication:** Bearer Token required (Admin)

#### Send Reminders:
**Request Body:**
```json
{
    "task_name": "send_reminders"
}
```

**Response:**
```json
{
    "message": "Task \"send_reminders\" executed",
    "task_result": {
        "success": true,
        "message": "Task completed successfully",
        "duration": 3.42,
        "timestamp": "2024-01-20T16:15:30Z"
    }
}
```

#### Reset Snoozes:
**Request Body:**
```json
{
    "task_name": "reset_daily_snoozes"
}
```

**Response:**
```json
{
    "message": "Task \"reset_daily_snoozes\" executed",
    "task_result": {
        "success": true,
        "message": "Task completed successfully",
        "duration": 0.67,
        "timestamp": "2024-01-20T16:15:45Z"
    }
}
```

---

## 🆕 Enhanced Alert Features

### Alert Creation with Advanced Options

**New Fields Available:**
- `starts_at`: Schedule alert for future delivery
- `expires_at`: Set expiration time for alerts
- `reminder_enabled`: Enable/disable reminders
- `is_archived`: Archive status
- Enhanced filtering and search capabilities

### Alert Status Types

- **Active**: Currently visible to users
- **Scheduled**: Created but not yet started
- **Expired**: Past expiration date
- **Archived**: Hidden from normal view
- **Inactive**: Manually deactivated

### Enhanced User Experience

- Users only see alerts that have started and are not archived
- Improved filtering options for admins
- Detailed tracking and analytics
- Better reminder management

---

## 🧪 Testing Guide

### Postman Environment Setup

Create environment variables:
```json
{
    "base_url": "http://localhost:8000/api",
    "admin_token": "",
    "user_token": "",
    "team_id": "",
    "alert_id": "",
    "user_id": ""
}
```

### Authentication Headers

For protected endpoints:
```
Authorization: Bearer {{admin_token}}
Content-Type: application/json
```

### Auto-save Tokens Script (Postman)

Add this to the Tests tab of your login request:
```javascript
if (pm.response.code === 200) {
    const responseJson = pm.response.json();
    pm.environment.set("access_token", responseJson.tokens.access);
    pm.environment.set("refresh_token", responseJson.tokens.refresh);
}
```

### Testing Scenarios

#### Scenario 1: Complete Alert Lifecycle
1. Create alert (as admin)
2. View alerts (as user) - should see new alert as unread
3. Mark as read (as user)
4. Snooze alert (as user)
5. View statistics (as admin)

#### Scenario 2: Team Management Workflow
1. Create a new team (as admin)
2. Assign users to the team
3. Create team-specific alert
4. Verify team members see the alert

#### Scenario 3: Notification Delivery Testing
1. Create alert with specific delivery type
2. Send notification manually
3. Check delivery status
4. Retry failed notifications

#### Scenario 4: Scheduler Management
1. Check scheduler status
2. Run task manually
3. Monitor execution results

### Common Test Cases

#### Permission Testing
- Try admin endpoints as regular user (should fail with 403)
- Try to access other user's personal alerts

#### Validation Testing
- Create alert with invalid data
- Test with past start times
- Test with invalid snooze durations

#### Edge Cases
- Empty states with no alerts
- Expired alerts behavior
- Archived alerts visibility

---

## 📁 Project Structure

```
atomicAds/
├── AlertingAndNotificationPlatform/
│   ├── migrations/                 # Database migrations
│   ├── management/
│   │   └── commands/
│   │       ├── create_seed_data.py # Seed data creation
│   │       ├── send_reminders.py   # Reminder scheduler
│   │       └── reset_daily_snoozes.py # Snooze reset
│   ├── notification/               # Notification system
│   │   ├── delivery/              # Delivery strategies
│   │   ├── factories/             # Factory patterns
│   │   └── observers/             # Observer patterns
│   ├── scheduler/                 # Background task scheduler
│   ├── admin.py                   # Django admin configuration
│   ├── models.py                  # Database models
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # API views
│   └── urls.py                    # URL patterns
├── atomicAds/
│   ├── settings.py                # Django settings
│   └── urls.py                    # Main URL configuration
├── requirements.txt               # Python dependencies
└── README.md                     # This comprehensive guide
```

---

## ✅ Features Implemented

### Core Authentication
- ✅ JWT Authentication (Login, Logout, Token Refresh)
- ✅ User Registration with Email Validation
- ✅ Role-based Access (Admin/User)
- ✅ User Profile Management
- ✅ Password Change Functionality

### Team Management
- ✅ Complete Team CRUD Operations
- ✅ Team Member Assignment/Removal
- ✅ Team-based Alert Targeting

### Alert System
- ✅ Alert Creation with Advanced Options
- ✅ Multiple Visibility Types (Organization, Teams, Users)
- ✅ Alert Status Management (Active, Scheduled, Expired, Archived)
- ✅ User Alert Interactions (Read, Snooze, Unsnooze)
- ✅ Enhanced Filtering and Search
- ✅ Alert Statistics and Tracking

### Notification Delivery
- ✅ OOP-based Delivery System
- ✅ Multiple Delivery Channels (Email, SMS, In-App)
- ✅ Delivery Status Tracking
- ✅ Failed Notification Retry Mechanism
- ✅ Delivery Analytics

### Background Processing
- ✅ Reminder Scheduling System
- ✅ Automatic Snooze Reset
- ✅ Task Execution Monitoring
- ✅ Scheduler Control APIs

### Enhanced Features
- ✅ Alert Archiving
- ✅ Reminder Toggle Control
- ✅ Start/Expiry Time Management
- ✅ Comprehensive Analytics
- ✅ Advanced Filtering Options

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Permission Denied Errors
```json
{
    "error": "Only administrators can access this feature"
}
```
**Solution:** Ensure you're using admin token for admin-only endpoints

#### 2. Token Expired
```json
{
    "detail": "Given token not valid for any token type"
}
```
**Solution:** Use refresh token to get new access token

#### 3. SMS Service Not Configured
```json
{
    "error": "SMS service not configured"
}
```
**Solution:** Configure `SMS_API_URL` and `SMS_API_KEY` in Django settings

#### 4. Scheduler Not Running
**Solution:** Set `ENABLE_TASK_SCHEDULER=True` in Django settings

#### 5. Database Migration Needed
**Solution:** 
```bash
python manage.py makemigrations
python manage.py migrate
```

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Testing Tips

1. **Use environment variables** for dynamic values
2. **Set up pre-request scripts** to get fresh tokens
3. **Create test data** using: `python manage.py create_seed_data`
4. **Monitor Django logs** for debugging
5. **Test with different user roles**

### Performance Expectations

- **Team operations**: < 500ms response time
- **Notification sending**: < 2s per 10 recipients
- **Scheduler operations**: < 1s response time
- **Alert listing**: < 300ms with filters

---

## 🔧 Configuration

### Environment Variables

Set these in your Django settings:

```python
# Notification Settings
SMS_API_URL = "your_sms_service_url"
SMS_API_KEY = "your_sms_api_key"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Scheduler Settings
ENABLE_TASK_SCHEDULER = True

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### Cron Job Setup

For production, set up cron jobs for background tasks:

```bash
# Send reminders every 30 minutes
*/30 * * * * cd /path/to/project && python manage.py send_reminders

# Reset daily snoozes at midnight
0 0 * * * cd /path/to/project && python manage.py reset_daily_snoozes
```

---

## 🎯 Next Steps

This comprehensive platform provides a solid foundation for enterprise-level alerting and notification management. The system includes:

- **Complete Authentication System** with JWT tokens
- **Advanced Alert Management** with multiple visibility options
- **Robust Team Management** for organizational structure
- **Sophisticated Notification Delivery** with multiple channels
- **Background Task Scheduling** for automated operations
- **Comprehensive Analytics** for monitoring and optimization

The platform is production-ready and can be extended with additional features like:
- Real-time websocket notifications
- Advanced reporting and dashboards
- Integration with external services
- Mobile app support
- Audit logging

All APIs are thoroughly documented and tested, making it easy for developers to integrate and extend the system.

**Happy coding! 🚀**

