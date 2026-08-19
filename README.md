# DevTrack

DevTrack is a minimal Django backend API for tracking engineering issues.

## Technologies

- Python
- Django
- JSON
- Postman
- Git/GitHub

## How to Run

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start the server:

```bash
python manage.py runserver
```

Base URL:

```text
http://127.0.0.1:8000/
```

## API Endpoints

### Reporter

- `POST /api/reporters/` - Create a reporter
- `GET /api/reporters/` - Get all reporters
- `GET /api/reporters/?id=1` - Get reporter by ID

### Issue

- `POST /api/issues/` - Create an issue
- `GET /api/issues/` - Get all issues
- `GET /api/issues/?id=1` - Get issue by ID
- `GET /api/issues/?status=open` - Filter issues by status

## OOP Design

`BaseEntity` is an abstract base class containing `validate()` and `to_dict()`.

`Reporter` and `Issue` inherit from `BaseEntity`.

`CriticalIssue` and `LowPriorityIssue` inherit from `Issue` and override `describe()`.

For critical issues:

```text
[URGENT] Login button not working on mobile — needs immediate attention
```

For low priority issues:

```text
Update footer text — low priority, handle when free
```

Medium and high priority issues use the base `Issue.describe()` implementation.

## Data Storage

The application uses:

- `reporters.json`
- `issues.json`

The one-to-many relationship is represented by storing `reporter_id` inside each issue.

## Example Request

### Create Reporter

```json
{
    "id": 1,
    "name": "Neel Sharma",
    "email": "neel@example.com",
    "team": "backend"
}
```

### Create Critical Issue

```json
{
    "id": 1,
    "title": "Login button not working on mobile",
    "description": "Users on iOS 17 cannot tap the login button",
    "status": "open",
    "priority": "critical",
    "reporter_id": 1
}
```

Expected response:

```json
{
    "id": 1,
    "title": "Login button not working on mobile",
    "description": "Users on iOS 17 cannot tap the login button",
    "status": "open",
    "priority": "critical",
    "reporter_id": 1,
    "message": "[URGENT] Login button not working on mobile — needs immediate attention"
}
```

## Validation Example

Sending an empty title:

```json
{
    "id": 2,
    "title": "",
    "description": "Something is broken",
    "status": "open",
    "priority": "high",
    "reporter_id": 1
}
```

Returns:

```json
{
    "error": "Title cannot be empty"
}
```

HTTP status: `400 Bad Request`

## Design Decision

JSON files were used instead of Django ORM because the assignment explicitly requires `issues.json` and `reporters.json`. This keeps the implementation simple while demonstrating OOP, inheritance, validation, JSON persistence, and API routing.

## Postman Testing

Before submission, test the endpoints in Postman and add screenshots here:

### Successful Request

_Add screenshot of a successful POST request._

### Validation Failure

_Add screenshot of a failed POST request showing HTTP 400._

### 404 Not Found

_Add screenshot of a GET request for a non-existent issue._
