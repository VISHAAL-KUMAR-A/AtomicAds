# NEW APIs POSTMAN TESTING GUIDE

## 🚀 AtomicAds Enhanced Features - API Testing Guide

This guide covers all the **NEW APIs** that have been implemented to address the critical missing features:

### 📋 **What's Been Added:**
1. **Team Management APIs** - Complete CRUD operations
2. **Notification Delivery System** - OOP-based delivery with Strategy, Factory, Observer patterns
3. **Reminder Scheduling System** - Background task management
4. **Enhanced Alert Management** - Improved functionality

---

## 📁 **POSTMAN COLLECTION SETUP**

### 🔧 **Environment Variables**
Create a new environment in Postman with these variables:

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

### 🔐 **Authentication Setup**
All new endpoints require authentication. Add this to your request headers:

```
Authorization: Bearer {{admin_token}}
Content-Type: application/json
```

---

## 🏢 **TEAM MANAGEMENT APIs**

### 1. **List All Teams**
```http
GET {{base_url}}/teams/
Authorization: Bearer {{admin_token}}
```

**Expected Response:**
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

### 2. **Create New Team** (Admin Only)
```http
POST {{base_url}}/teams/
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "name": "Marketing Team",
  "description": "Marketing and communications team"
}
```

**Expected Response:**
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

### 3. **Get Team Details**
```http
GET {{base_url}}/teams/{{team_id}}/
Authorization: Bearer {{admin_token}}
```

**Expected Response:**
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
    },
    {
      "id": 3,
      "email": "jane.smith@company.com",
      "full_name": "Jane Smith",
      "role": "user",
      "is_active": true
    }
  ]
}
```

### 4. **Update Team** (Admin Only)
```http
PUT {{base_url}}/teams/{{team_id}}/
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "name": "Senior Engineering Team",
  "description": "Senior software development and architecture team"
}
```

### 5. **Delete Team** (Admin Only)
```http
DELETE {{base_url}}/teams/{{team_id}}/
Authorization: Bearer {{admin_token}}
```

**Expected Response:**
```json
{
  "message": "Team deleted successfully"
}
```

### 6. **Manage Team Members** (Admin Only)

#### **Assign Users to Team:**
```http
POST {{base_url}}/teams/{{team_id}}/members/
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "user_ids": [2, 3, 4],
  "action": "assign"
}
```

**Expected Response:**
```json
{
  "message": "Successfully assigned 3 users to team Engineering",
  "team_id": 1,
  "team_name": "Engineering",
  "action": "assign",
  "affected_users": 3
}
```

#### **Remove Users from Team:**
```http
POST {{base_url}}/teams/{{team_id}}/members/
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "user_ids": [2, 3],
  "action": "remove"
}
```

**Expected Response:**
```json
{
  "message": "Successfully removed 2 users from team Engineering",
  "team_id": 1,
  "team_name": "Engineering",
  "action": "remove",
  "affected_users": 2
}
```

#### **Get Team Member Details:**
```http
GET {{base_url}}/teams/{{team_id}}/members/
Authorization: Bearer {{admin_token}}
```

---

## 📬 **NOTIFICATION DELIVERY APIs**

### 1. **Send Manual Notification** (Admin Only)
```http
POST {{base_url}}/alerts/{{alert_id}}/send-notification/
Authorization: Bearer {{admin_token}}
Content-Type: application/json
```

**Expected Response:**
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

### 2. **Check Delivery Status** (Admin Only)
```http
GET {{base_url}}/alerts/{{alert_id}}/delivery-status/
Authorization: Bearer {{admin_token}}
```

**Expected Response:**
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

### 3. **Retry Failed Notifications** (Admin Only)
```http
POST {{base_url}}/alerts/{{alert_id}}/retry-notifications/
Authorization: Bearer {{admin_token}}
Content-Type: application/json
```

**Expected Response:**
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
    },
    {
      "delivery_id": 17,
      "user_email": "bob.johnson@company.com",
      "status": "failed",
      "attempt_count": 2,
      "error": "Invalid email address"
    }
  ]
}
```

---

## ⏰ **SCHEDULER MANAGEMENT APIs**

### 1. **Get Scheduler Status** (Admin Only)
```http
GET {{base_url}}/scheduler/status/
Authorization: Bearer {{admin_token}}
```

**Expected Response:**
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
      },
      "reset_daily_snoozes": {
        "name": "reset_daily_snoozes",
        "command": "reset_daily_snoozes",
        "interval_minutes": 1440,
        "enabled": true,
        "last_run": "2024-01-20T01:00:00Z",
        "next_run": "2024-01-21T01:00:00Z",
        "execution_count": 20,
        "failure_count": 0,
        "last_result": {
          "success": true,
          "message": "Task completed successfully",
          "duration": 0.85,
          "timestamp": "2024-01-20T01:00:00Z"
        }
      }
    },
    "recent_executions": [
      {
        "task_name": "send_reminders",
        "success": true,
        "message": "Task completed successfully",
        "duration": 2.35,
        "timestamp": "2024-01-20T15:30:00Z"
      }
    ]
  },
  "cron_setup_guide": "# AtomicAds Notification System - Cron Job Setup Guide\n\n# Add these lines to your crontab...\n*/30 * * * * cd /path/to/your/project && python manage.py send_reminders --max-reminders 100\n..."
}
```

### 2. **Control Scheduler** (Admin Only)

#### **Start Scheduler:**
```http
POST {{base_url}}/scheduler/control/
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "action": "start"
}
```

**Expected Response:**
```json
{
  "message": "Scheduler started successfully",
  "action": "start",
  "scheduler_running": true
}
```

#### **Stop Scheduler:**
```http
POST {{base_url}}/scheduler/control/
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "action": "stop"
}
```

**Expected Response:**
```json
{
  "message": "Scheduler stopped successfully",
  "action": "stop",
  "scheduler_running": false
}
```

### 3. **Run Task Manually** (Admin Only)

#### **Send Reminders Now:**
```http
POST {{base_url}}/scheduler/run-task/
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "task_name": "send_reminders"
}
```

**Expected Response:**
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

#### **Reset Snoozes Now:**
```http
POST {{base_url}}/scheduler/run-task/
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "task_name": "reset_daily_snoozes"
}
```

**Expected Response:**
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

## 🧪 **TESTING SCENARIOS**

### **Scenario 1: Complete Team Management Workflow**

1. **Create a new team** (as admin)
2. **Get team details** to verify creation
3. **Assign users to the team**
4. **Verify team membership** via team details endpoint
5. **Update team information**
6. **Remove some users from team**
7. **Delete team** (optional)

### **Scenario 2: Notification Delivery Testing**

1. **Create an alert** with specific delivery type (email/sms/in_app)
2. **Send notification manually** for the alert
3. **Check delivery status** to see results
4. **If there are failures, retry failed notifications**
5. **Verify delivery logs** are properly recorded

### **Scenario 3: Scheduler Management Testing**

1. **Check initial scheduler status**
2. **Run a task manually** to test execution
3. **Stop the scheduler**
4. **Try to run tasks while stopped**
5. **Start the scheduler again**
6. **Monitor task execution** through status endpoint

### **Scenario 4: End-to-End Alert with Reminders**

1. **Create alert** with reminder_enabled=true
2. **Send initial notification**
3. **Wait for reminder interval** (or trigger manually)
4. **Check that reminders are sent** to users who haven't read
5. **Mark alert as read** for some users
6. **Verify reminders stop** for those users

---

## 🚨 **ERROR HANDLING EXAMPLES**

### **403 Forbidden (Non-Admin User):**
```json
{
  "error": "Only administrators can create teams"
}
```

### **404 Not Found:**
```json
{
  "error": "Team not found"
}
```

### **400 Bad Request:**
```json
{
  "error": "Invalid user IDs: [999, 1000]"
}
```

### **500 Internal Server Error:**
```json
{
  "error": "SMS service not configured"
}
```

---

## 📊 **TESTING CHECKLIST**

### ✅ **Team Management**
- [ ] List teams (authenticated user)
- [ ] Create team (admin only)
- [ ] Get team details with members
- [ ] Update team information (admin only)
- [ ] Delete team (admin only)
- [ ] Assign users to team (admin only)
- [ ] Remove users from team (admin only)
- [ ] Error handling for non-existent teams
- [ ] Error handling for non-admin users

### ✅ **Notification Delivery**
- [ ] Send email notifications
- [ ] Send SMS notifications (if configured)
- [ ] Send in-app notifications
- [ ] Check delivery status and logs
- [ ] Retry failed notifications
- [ ] Handle users without phone numbers
- [ ] Verify delivery statistics
- [ ] Test notification metadata

### ✅ **Scheduler Management**
- [ ] Get scheduler status
- [ ] Start/stop scheduler
- [ ] Run tasks manually
- [ ] Monitor task execution history
- [ ] Handle task failures gracefully
- [ ] Verify cron setup guide

### ✅ **Integration Testing**
- [ ] Create alert → Send notification → Check delivery
- [ ] Team assignment → Alert targeting → Notification delivery
- [ ] Reminder scheduling → Automatic execution
- [ ] Failed delivery → Retry mechanism

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

1. **"Permission Denied" errors:**
   - Ensure you're using admin token for admin-only endpoints
   - Check token expiration

2. **"SMS service not configured" errors:**
   - Configure SMS_API_URL and SMS_API_KEY in Django settings
   - Or test with email/in_app delivery types

3. **Scheduler not running:**
   - Set ENABLE_TASK_SCHEDULER=True in Django settings
   - Or control via API endpoints

4. **Database migration needed:**
   - Run: `python manage.py makemigrations`
   - Run: `python manage.py migrate`

### **Testing Tips:**

1. **Use environment variables** for dynamic values (team_id, alert_id, etc.)
2. **Set up pre-request scripts** to get fresh tokens
3. **Create test data** using seed commands: `python manage.py create_seed_data`
4. **Monitor Django logs** for debugging information
5. **Test with different user roles** (admin vs regular user)

---

## 🎯 **PERFORMANCE TESTING**

### **Load Testing Scenarios:**

1. **Bulk notification sending:**
   - Create alert with 100+ recipients
   - Send notification and monitor delivery time

2. **Concurrent team operations:**
   - Multiple team creations/updates simultaneously

3. **Scheduler stress test:**
   - Run multiple tasks concurrently
   - Monitor system resources

### **Expected Performance:**
- **Team operations:** < 500ms response time
- **Notification sending:** < 2s per 10 recipients
- **Scheduler operations:** < 1s response time

---

This guide provides comprehensive testing coverage for all new APIs. Start with the basic CRUD operations, then move to complex integration scenarios to fully validate the enhanced notification system! 🚀
