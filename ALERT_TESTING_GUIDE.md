# Alert System Testing Guide - Postman

This guide explains how to test the complete alert system using Postman. The alert system allows administrators to create alerts with different visibility levels and users to interact with those alerts.

## Table of Contents
1. [Setup and Authentication](#setup-and-authentication)
2. [Team Management](#team-management)
3. [Alert Management (Admin)](#alert-management-admin)
4. [User Alert Interactions](#user-alert-interactions)
5. [Alert Statistics](#alert-statistics)
6. [Testing Scenarios](#testing-scenarios)

## Setup and Authentication

### 1. Start the Django Server
```bash
python manage.py runserver
```
The server will run on `http://127.0.0.1:8000/`

### 2. Base URL
Set your base URL in Postman environment:
- Variable: `base_url`
- Value: `http://127.0.0.1:8000/auth`

### 3. Create Test Users

#### Register an Admin User
- **Method**: POST
- **URL**: `{{base_url}}/register/`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
    "username": "admin_user",
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
    "phone_number": "+1234567890"
}
```

#### Register Regular Users
- **Method**: POST
- **URL**: `{{base_url}}/register/`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "phone_number": "+1234567891"
}
```

```json
{
    "username": "jane_smith",
    "email": "jane@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "user",
    "phone_number": "+1234567892"
}
```

### 4. Login and Get Tokens

#### Admin Login
- **Method**: POST
- **URL**: `{{base_url}}/login/`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
    "email": "admin@example.com",
    "password": "SecurePassword123!"
}
```

Save the `access` token from the response as `admin_token` in your environment.

#### User Login
- **Method**: POST
- **URL**: `{{base_url}}/login/`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
    "email": "john@example.com",
    "password": "SecurePassword123!"
}
```

Save the `access` token from the response as `user_token` in your environment.

## Team Management

### Create Teams (Admin Only)
Create teams first to test team-specific alerts.

#### Create Engineering Team
- **Method**: POST
- **URL**: `{{base_url}}/teams/` (Note: You'll need to create this endpoint or use Django admin)
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{admin_token}}`

For now, you can create teams via Django admin panel or directly in the database.

## Alert Management (Admin)

### 1. Create Organization-Wide Alert
- **Method**: POST
- **URL**: `{{base_url}}/alerts/`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{admin_token}}`
- **Body** (raw JSON):
```json
{
    "title": "System Maintenance Alert",
    "message_body": "The system will be under maintenance from 2:00 AM to 4:00 AM UTC. Please save your work and logout before this time.",
    "severity": "warning",
    "delivery_type": "in_app",
    "reminder_frequency": 2,
    "visibility_type": "organization"
}
```

### 2. Create Team-Specific Alert
- **Method**: POST
- **URL**: `{{base_url}}/alerts/`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{admin_token}}`
- **Body** (raw JSON):
```json
{
    "title": "Engineering Team: New Deployment",
    "message_body": "A new version of the application has been deployed to staging environment. Please test your features.",
    "severity": "info",
    "delivery_type": "in_app",
    "reminder_frequency": 4,
    "visibility_type": "teams",
    "recipient_teams": [1]
}
```

### 3. Create User-Specific Alert
- **Method**: POST
- **URL**: `{{base_url}}/alerts/`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{admin_token}}`
- **Body** (raw JSON):
```json
{
    "title": "Personal: Account Review Required",
    "message_body": "Your account requires a security review. Please contact the administrator.",
    "severity": "critical",
    "delivery_type": "in_app",
    "reminder_frequency": 1,
    "visibility_type": "users",
    "recipient_users": [2]
}
```

### 4. Create Alert with Expiration
- **Method**: POST
- **URL**: `{{base_url}}/alerts/`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{admin_token}}`
- **Body** (raw JSON):
```json
{
    "title": "Limited Time Offer",
    "message_body": "Special promotion valid until tomorrow!",
    "severity": "info",
    "delivery_type": "in_app",
    "reminder_frequency": 2,
    "visibility_type": "organization",
    "expires_at": "2025-09-21T23:59:59Z"
}
```

### 5. List All Alerts (Admin View)
- **Method**: GET
- **URL**: `{{base_url}}/alerts/`
- **Headers**: 
  - `Authorization: Bearer {{admin_token}}`

### 6. Get Alert Details
- **Method**: GET
- **URL**: `{{base_url}}/alerts/1/`
- **Headers**: 
  - `Authorization: Bearer {{admin_token}}`

### 7. Update Alert
- **Method**: PATCH
- **URL**: `{{base_url}}/alerts/1/`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{admin_token}}`
- **Body** (raw JSON):
```json
{
    "title": "Updated: System Maintenance Alert",
    "message_body": "The maintenance window has been moved to 3:00 AM to 5:00 AM UTC."
}
```

### 8. Delete Alert (Soft Delete)
- **Method**: DELETE
- **URL**: `{{base_url}}/alerts/1/`
- **Headers**: 
  - `Authorization: Bearer {{admin_token}}`

## User Alert Interactions

### 1. View My Alerts
- **Method**: GET
- **URL**: `{{base_url}}/my-alerts/`
- **Headers**: 
  - `Authorization: Bearer {{user_token}}`

#### Filter Alerts
- **Unread alerts**: `{{base_url}}/my-alerts/?read=false`
- **Read alerts**: `{{base_url}}/my-alerts/?read=true`
- **Critical alerts**: `{{base_url}}/my-alerts/?severity=critical`
- **Warning alerts**: `{{base_url}}/my-alerts/?severity=warning`

### 2. Mark Alert as Read
- **Method**: POST
- **URL**: `{{base_url}}/alerts/1/read/`
- **Headers**: 
  - `Authorization: Bearer {{user_token}}`

### 3. Snooze Alert
- **Method**: POST
- **URL**: `{{base_url}}/alerts/1/snooze/`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{user_token}}`
- **Body** (raw JSON):
```json
{
    "hours": 4
}
```

### 4. Unsnooze Alert
- **Method**: POST
- **URL**: `{{base_url}}/alerts/1/unsnooze/`
- **Headers**: 
  - `Authorization: Bearer {{user_token}}`

## Alert Statistics

### Get Alert Statistics (Admin Only)
- **Method**: GET
- **URL**: `{{base_url}}/alerts/stats/`
- **Headers**: 
  - `Authorization: Bearer {{admin_token}}`

## Testing Scenarios

### Scenario 1: Complete Alert Lifecycle

1. **Create alert** (as admin)
2. **View alerts** (as user) - should see new alert as unread
3. **Mark as read** (as user)
4. **View alerts** (as user) - alert should now be marked as read
5. **Snooze alert** (as user)
6. **View alerts** (as user) - alert should be snoozed
7. **Unsnooze alert** (as user)
8. **View statistics** (as admin) - see interaction data

### Scenario 2: Permission Testing

1. **Try to create alert as regular user** - should fail with 403
2. **Try to view other user's personal alerts** - should not see them
3. **Try to access admin statistics as user** - should fail with 403

### Scenario 3: Visibility Testing

1. **Create organization alert** (as admin)
2. **Login as different users** - all should see the alert
3. **Create team-specific alert** (as admin)
4. **Login as team member** - should see the alert
5. **Login as non-team member** - should NOT see the alert

### Scenario 4: Expiration Testing

1. **Create alert with past expiration date** - should fail validation
2. **Create alert with future expiration** - should succeed
3. **View alert details** - `is_expired` should be false initially

## Error Testing

### Test Invalid Data

#### Invalid Alert Creation
- **Method**: POST
- **URL**: `{{base_url}}/alerts/`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{admin_token}}`
- **Body** (raw JSON):
```json
{
    "title": "",
    "message_body": "Test",
    "severity": "invalid_severity",
    "visibility_type": "teams"
}
```
Should return validation errors.

#### Invalid Snooze Duration
- **Method**: POST
- **URL**: `{{base_url}}/alerts/1/snooze/`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{user_token}}`
- **Body** (raw JSON):
```json
{
    "hours": 200
}
```
Should fail validation (max 168 hours).

## Response Examples

### Successful Alert Creation Response
```json
{
    "id": 1,
    "title": "System Maintenance Alert",
    "message_body": "The system will be under maintenance...",
    "severity": "warning",
    "delivery_type": "in_app",
    "reminder_frequency": 2,
    "visibility_type": "organization",
    "is_active": true,
    "expires_at": null,
    "created_by": 1,
    "created_by_name": "Admin User",
    "recipients": [],
    "is_expired": false,
    "created_at": "2025-09-19T12:00:00Z",
    "updated_at": "2025-09-19T12:00:00Z"
}
```

### User Alerts Response
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
            "delivery_type": "in_app",
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

## Tips for Testing

1. **Use Postman Environment Variables** for tokens and IDs to make testing easier
2. **Test with multiple users** to verify visibility rules
3. **Check the Django admin panel** to see database entries
4. **Monitor server logs** for any errors
5. **Test edge cases** like expired alerts and invalid data
6. **Use Postman Collections** to save and organize your tests

## Common Issues and Solutions

1. **401 Unauthorized**: Check that your token is valid and properly formatted in the Authorization header
2. **403 Forbidden**: Ensure the user has the correct permissions (admin vs regular user)
3. **404 Not Found**: Verify the alert ID exists and the user has access to it
4. **400 Bad Request**: Check request body format and required fields
5. **500 Internal Server Error**: Check Django server logs for detailed error information

This completes the comprehensive testing guide for the Alert System!
