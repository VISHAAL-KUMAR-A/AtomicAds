# AtomicAds - Alerting & Notification Platform

A Django REST API based alerting and notification platform with JWT authentication.

## Quick Setup

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

The API will be available at: `http://127.0.0.1:8000/api/auth/`

## Test Accounts

After running the seed data command, you can use these test accounts:

### Admin Users:
- **Email:** `admin@atomicads.com` | **Password:** `admin123456`
- **Email:** `alice.brown@atomicads.com` | **Password:** `user123456`

### Regular Users:
- **Email:** `john.doe@atomicads.com` | **Password:** `user123456`
- **Email:** `jane.smith@atomicads.com` | **Password:** `user123456`
- **Email:** `bob.wilson@atomicads.com` | **Password:** `user123456`

## API Endpoints

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password
- `GET /api/auth/dashboard/` - User dashboard
- `GET /api/auth/teams/` - List all teams

## Testing with Postman

See `POSTMAN_TESTING_GUIDE.md` for detailed testing instructions and examples.

## Features Implemented

✅ JWT Authentication (Login, Logout, Token Refresh)  
✅ User Registration with Email Validation  
✅ Role-based Access (Admin/User)  
✅ Team Management  
✅ User Profile Management  
✅ Password Change Functionality  
✅ Comprehensive API Documentation  
✅ Seed Data for Testing  
✅ Django Admin Integration  

## Project Structure

```
atomicAds/
├── AlertingAndNotificationPlatform/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── create_seed_data.py
│   ├── admin.py          # Django admin configuration
│   ├── models.py         # User and Team models
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   └── urls.py           # URL patterns
├── atomicAds/
│   ├── settings.py       # Django settings with JWT config
│   └── urls.py           # Main URL configuration
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── POSTMAN_TESTING_GUIDE.md  # Postman testing guide
```

## Next Steps

This authentication system is ready to be extended with the alerting and notification features as outlined in the PRD. The foundation includes:

- User management with roles
- Team organization  
- JWT-based secure authentication
- Extensible Django REST Framework setup
- Comprehensive testing setup

You can now build upon this foundation to implement the alerting system features.
