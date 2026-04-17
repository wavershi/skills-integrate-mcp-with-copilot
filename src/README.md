# Mergington High School Activities API

FastAPI app for activities, authentication, role management, and club membership.

## Features

- User registration and login
- Token-based session management
- Role model support: user, admin, super_admin
- Protected routes for authenticated flows
- Clubs directory with join state
- Membership listing for current user

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   uvicorn app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

Authentication:

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | /auth/register | Register a new user account |
| POST | /auth/login | Login and receive a bearer token |
| POST | /auth/logout | Logout and invalidate current token |
| GET | /auth/me | Get current authenticated user profile |

Clubs and memberships:

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | /clubs | Get club directory with Join or Joined state |
| POST | /clubs/{club_name}/join | Join a club as current user |
| GET | /memberships | List memberships for current user |

Activities (authenticated):

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | /activities | Get all activities |
| POST | /activities/{activity_name}/signup | Sign up current user for an activity |
| DELETE | /activities/{activity_name}/unregister | Unregister current user from an activity |

## Notes

- Send bearer tokens in Authorization header for protected routes.
- Session token persistence in the frontend uses browser local storage.
- All data is in-memory and resets on server restart.
