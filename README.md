# Cubic Backend

## Authentication

Cubic Backend supports Google OAuth for Students and Teachers.

### Admin login (username/password)

For administrative access without Google OAuth, configure the following environment variables (e.g., in `env.local`):

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme
# optional profile fields
ADMIN_EMAIL=admin@example.com
ADMIN_FIRST_NAME=Admin
ADMIN_LAST_NAME=User
```

Then authenticate via:

- Endpoint: `POST /api/auth/admin/login`
- Body:
	```json
	{ "username": "admin", "password": "changeme" }
	```

On success you will receive the same `AuthResponse` as Google auth with a JWT token and a user of role `admin`.
