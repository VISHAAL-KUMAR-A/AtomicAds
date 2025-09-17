# JWT Authentication API - Postman Testing Guide

This guide will help you test the JWT authentication system using Postman.

## Base URL
```
http://127.0.0.1:8000/api/auth/
```

## Prerequisites

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Create seed data:
   ```bash
   python manage.py create_seed_data
   ```

4. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### 1. User Registration
**Endpoint:** `POST /api/auth/register/`
**Authentication:** None required

**Request Body (JSON):**
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

**Expected Response (201 Created):**
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

**Request Body (JSON):**
```json
{
    "email": "admin@atomicads.com",
    "password": "admin123456"
}
```

**Expected Response (200 OK):**
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

**Request Body (JSON):**
```json
{
    "refresh": "your_refresh_token_here"
}
```

**Expected Response (200 OK):**
```json
{
    "access": "new_access_token_here"
}
```

### 4. User Logout
**Endpoint:** `POST /api/auth/logout/`
**Authentication:** Bearer Token required

**Headers:**
```
Authorization: Bearer your_access_token_here
```

**Request Body (JSON):**
```json
{
    "refresh": "your_refresh_token_here"
}
```

**Expected Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

### 5. User Profile
**Endpoint:** `GET /api/auth/profile/`
**Authentication:** Bearer Token required

**Headers:**
```
Authorization: Bearer your_access_token_here
```

**Expected Response (200 OK):**
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

**Headers:**
```
Authorization: Bearer your_access_token_here
```

**Request Body (JSON):**
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

**Headers:**
```
Authorization: Bearer your_access_token_here
```

**Request Body (JSON):**
```json
{
    "old_password": "current_password",
    "new_password": "new_secure_password123",
    "confirm_new_password": "new_secure_password123"
}
```

**Expected Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

### 8. User Dashboard
**Endpoint:** `GET /api/auth/dashboard/`
**Authentication:** Bearer Token required

**Headers:**
```
Authorization: Bearer your_access_token_here
```

**Expected Response (200 OK):**
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

**Headers:**
```
Authorization: Bearer your_access_token_here
```

**Expected Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Engineering",
        "description": "Software development and technical operations team",
        "created_at": "2025-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "name": "Marketing",
        "description": "Marketing and communications team",
        "created_at": "2025-01-01T00:00:00Z"
    }
]
```

## Postman Setup Steps

### 1. Create a New Collection
1. Open Postman
2. Click "New" → "Collection"
3. Name it "AtomicAds Authentication API"

### 2. Set up Environment Variables
1. Click on "Environments" in the left sidebar
2. Click "Create Environment"
3. Name it "AtomicAds Dev"
4. Add the following variables:
   - `base_url`: `http://127.0.0.1:8000/api/auth`
   - `access_token`: (leave empty, will be filled automatically)
   - `refresh_token`: (leave empty, will be filled automatically)

### 3. Create Requests

For each endpoint above:
1. Click "Add Request" in your collection
2. Set the HTTP method (GET, POST, PATCH)
3. Set the URL using `{{base_url}}/endpoint`
4. Add headers if required
5. Add request body if required

### 4. Authentication Setup

#### For endpoints requiring authentication:
1. Go to the "Authorization" tab
2. Select "Bearer Token"
3. Enter `{{access_token}}` in the token field

#### Auto-save tokens from login response:
1. In the login request, go to the "Tests" tab
2. Add this script:
```javascript
if (pm.response.code === 200) {
    const responseJson = pm.response.json();
    pm.environment.set("access_token", responseJson.tokens.access);
    pm.environment.set("refresh_token", responseJson.tokens.refresh);
}
```

## Testing Workflow

### 1. Test User Registration
1. Send a POST request to `/register/` with user data
2. Verify you get a 201 status code and tokens
3. Save the tokens for future use

### 2. Test User Login
1. Send a POST request to `/login/` with credentials
2. Verify you get a 200 status code and tokens
3. The tokens should be automatically saved if you added the test script

### 3. Test Protected Endpoints
1. Use the saved access token to call protected endpoints
2. Test `/profile/`, `/dashboard/`, `/teams/`

### 4. Test Token Refresh
1. Wait for the access token to expire (or modify the expiry time in settings)
2. Use the refresh token to get a new access token

### 5. Test Logout
1. Send a POST request to `/logout/` with the refresh token
2. Verify the token is blacklisted
3. Try using the old tokens - they should fail

## Predefined Test Accounts

After running the seed data command, you can use these accounts:

### Admin Accounts:
- **Email:** `admin@atomicads.com` | **Password:** `admin123456`
- **Email:** `alice.brown@atomicads.com` | **Password:** `user123456`

### Regular User Accounts:
- **Email:** `john.doe@atomicads.com` | **Password:** `user123456`
- **Email:** `jane.smith@atomicads.com` | **Password:** `user123456`
- **Email:** `bob.wilson@atomicads.com` | **Password:** `user123456`

## Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

## Troubleshooting

### Token Expired Error
```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```
**Solution:** Use the refresh token to get a new access token.

### Invalid Credentials
```json
{
    "email": ["Invalid email or password."]
}
```
**Solution:** Check the email and password are correct.

### Validation Errors
```json
{
    "email": ["A user with this email already exists."],
    "password": ["This password is too short. It must contain at least 8 characters."]
}
```
**Solution:** Fix the validation errors and try again.
