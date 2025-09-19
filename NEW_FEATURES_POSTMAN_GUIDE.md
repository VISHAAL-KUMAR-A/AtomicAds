# New Alert Management Features - Postman Testing Guide

This guide covers testing the new alert management features that have been added to the AtomicAds alerting platform. These features include alert archiving, enhanced filtering, reminder toggling, start/expiry times, and detailed tracking.

## Prerequisites

1. **Environment Setup**: Ensure you have a Postman environment set up with:
   - `{{base_url}}`: Your Django server URL (e.g., `http://localhost:8000`)
   - `{{access_token}}`: JWT access token for authentication

2. **Authentication**: All endpoints require authentication. Use the Bearer token format:
   ```
   Authorization: Bearer {{access_token}}
   ```

3. **Admin Access**: Most new features require admin privileges. Ensure you're testing with an admin account.

## New API Endpoints

### 1. Enhanced Alert Creation with Start Time and Reminders

**Endpoint**: `POST {{base_url}}/api/alerts/`

**Description**: Create alerts with new fields including start time, expiry time, and reminder settings.

**Request Body**:
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
    "expires_at": "2024-01-16T06:00:00Z"
}
```

**Test Cases**:
- ✅ Valid alert creation with start and end times
- ✅ Alert creation without start time (should default to immediate)
- ❌ Start time in the past (should fail)
- ❌ End time before start time (should fail)
- ❌ Non-admin user creating alert (should fail with 403)

---

### 2. Enhanced Alert Listing with Filtering

**Endpoint**: `GET {{base_url}}/api/alerts/`

**Description**: List alerts with enhanced filtering options for admin users.

**Query Parameters**:
- `status`: `active`, `expired`, `scheduled`, `archived`, `inactive`
- `severity`: `info`, `warning`, `critical`
- `audience`: `organization`, `teams`, `users`
- `created_by`: User ID
- `start_date`: ISO datetime
- `end_date`: ISO datetime

**Test Examples**:

1. **Filter by Status (Active Alerts)**:
   ```
   GET {{base_url}}/api/alerts/?status=active
   ```

2. **Filter by Severity and Status**:
   ```
   GET {{base_url}}/api/alerts/?severity=critical&status=active
   ```

3. **Filter by Date Range**:
   ```
   GET {{base_url}}/api/alerts/?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z
   ```

4. **Filter by Audience Type**:
   ```
   GET {{base_url}}/api/alerts/?audience=organization
   ```

**Test Cases**:
- ✅ Admin user can filter by all parameters
- ✅ Non-admin user sees only their own alerts
- ✅ Multiple filters work together
- ✅ Invalid filter values are ignored gracefully

---

### 3. Archive/Unarchive Alerts

**Endpoint**: `POST {{base_url}}/api/alerts/{alert_id}/archive/`

**Description**: Archive or unarchive alerts (admin only).

**Request Body**:
```json
{
    "is_archived": true
}
```

**Test Examples**:

1. **Archive an Alert**:
   ```json
   {
       "is_archived": true
   }
   ```

2. **Unarchive an Alert**:
   ```json
   {
       "is_archived": false
   }
   ```

**Expected Response**:
```json
{
    "message": "Alert archived successfully",
    "alert_id": 123,
    "is_archived": true
}
```

**Test Cases**:
- ✅ Admin can archive active alert
- ✅ Admin can unarchive archived alert
- ❌ Non-admin user cannot archive (should fail with 403)
- ❌ Invalid alert ID (should fail with 404)

---

### 4. Toggle Alert Reminders

**Endpoint**: `POST {{base_url}}/api/alerts/{alert_id}/toggle-reminder/`

**Description**: Enable or disable reminders for an alert (admin only).

**Request**: No body required (toggles current state)

**Expected Response**:
```json
{
    "message": "Alert reminders enabled successfully",
    "alert_id": 123,
    "reminder_enabled": true
}
```

**Test Cases**:
- ✅ Admin can toggle reminders from enabled to disabled
- ✅ Admin can toggle reminders from disabled to enabled
- ❌ Non-admin user cannot toggle reminders (should fail with 403)
- ❌ Invalid alert ID (should fail with 404)

---

### 5. Alert Tracking and Statistics

**Endpoint**: `GET {{base_url}}/api/alerts/{alert_id}/tracking/`

**Description**: Get detailed tracking information for a specific alert (admin only).

**Expected Response**:
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

**Test Cases**:
- ✅ Admin can view tracking for any alert
- ✅ Correct percentage calculations
- ✅ Accurate snooze statistics
- ❌ Non-admin user cannot access tracking (should fail with 403)

---

### 6. Enhanced Alert Statistics

**Endpoint**: `GET {{base_url}}/api/alerts/stats/`

**Description**: Get comprehensive alert statistics including new metrics.

**Expected Response**:
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

**Test Cases**:
- ✅ Admin can access comprehensive statistics
- ✅ All new fields are included in response
- ✅ Calculations are accurate
- ❌ Non-admin user cannot access stats (should fail with 403)

---

### 7. Updated Alert Detail View

**Endpoint**: `GET {{base_url}}/api/alerts/{alert_id}/`

**Description**: View detailed alert information including new fields.

**Expected Response Fields** (new additions):
```json
{
    "id": 123,
    "title": "System Alert",
    "is_archived": false,
    "starts_at": "2024-01-15T18:00:00Z",
    "expires_at": "2024-01-16T06:00:00Z",
    "reminder_enabled": true,
    "is_expired": false,
    "is_started": true,
    "is_currently_active": true,
    "status": "active",
    // ... other existing fields
}
```

---

### 8. User Alert List (Updated)

**Endpoint**: `GET {{base_url}}/api/my-alerts/`

**Description**: Users now only see alerts that have started and are not archived.

**Test Cases**:
- ✅ Users don't see scheduled alerts (not yet started)
- ✅ Users don't see archived alerts
- ✅ Users see alerts with new status information

---

## Testing Workflow

### 1. Setup Test Data

1. **Create Admin User**: Register or login as admin
2. **Create Test Alerts**: Create alerts with various configurations:
   - Immediate alerts (no start time)
   - Scheduled alerts (future start time)
   - Expiring alerts (with end time)
   - Alerts with reminders disabled

### 2. Test Alert Management Features

1. **Create Alerts**: Test all variations of alert creation
2. **List and Filter**: Test all filter combinations
3. **Archive**: Test archiving and unarchiving
4. **Toggle Reminders**: Test enabling/disabling reminders
5. **Track Interactions**: View detailed tracking information

### 3. Test User Experience

1. **User View**: Test how regular users see alerts
2. **Snooze Behavior**: Test snoozing and its effect on tracking
3. **Read Status**: Test marking alerts as read and statistics

### 4. Test Edge Cases

1. **Permissions**: Ensure non-admins cannot access admin endpoints
2. **Invalid Data**: Test with invalid alert IDs, dates, etc.
3. **Empty States**: Test behavior with no alerts or recipients

## Common Error Responses

### 403 Forbidden
```json
{
    "error": "Only administrators can access this feature"
}
```

### 404 Not Found
```json
{
    "error": "Alert not found"
}
```

### 400 Bad Request
```json
{
    "starts_at": ["starts_at must be in the future"],
    "expires_at": ["starts_at must be before expires_at"]
}
```

## Tips for Testing

1. **Use Variables**: Set up Postman environment variables for common values
2. **Test Sequences**: Create test sequences that build on each other
3. **Validation**: Always check response status codes and data structure
4. **Cleanup**: Archive or delete test alerts after testing
5. **Time Zones**: Be aware of timezone differences when testing datetime fields

## Sample Postman Collection Structure

```
Alert Management API Tests/
├── Authentication/
│   ├── Admin Login
│   └── User Login
├── Alert Creation/
│   ├── Create Basic Alert
│   ├── Create Scheduled Alert
│   ├── Create Alert with End Time
│   └── Invalid Alert Creation Tests
├── Alert Management/
│   ├── List Alerts with Filters
│   ├── Archive Alert
│   ├── Unarchive Alert
│   ├── Toggle Reminders
│   └── Get Alert Details
├── Admin Features/
│   ├── Alert Statistics
│   ├── Alert Tracking
│   └── Filtered Alert Lists
└── User Features/
    ├── My Alerts List
    ├── Mark Alert as Read
    └── Snooze Alert
```

This guide provides comprehensive testing coverage for all the new alert management features. Each endpoint should be tested with both valid and invalid data to ensure robust functionality.
