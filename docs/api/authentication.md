# Authentication API

## Login

```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword" 
}
```

Response:
```json
{ "key": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" } 
```

Use this token in all subsequent requests:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Logout

```http
POST /api/auth/logout/
Authorization: Token <token>
```

## Current User

```http
GET /api/auth/user/
Authorization: Token <token>
```

## Register

```http
POST /api/auth/registration/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password1": "strongpassword", 
  "password2": "strongpassword" 
}
```

## Password Change

```http
POST /api/auth/password/change/
Authorization: Token <token>

{
  "new_password1": "newpassword", 
  "new_password2": "newpassword" 
}
```
