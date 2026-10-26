# User Management API

A simple REST API for managing users, built with FastAPI and PostgreSQL using raw SQL (psycopg2). It supports creating, listing, updating and deleting users, and is tested through Swagger UI.

## Features

- Create a user
- List all users
- Update a user
- Delete a user
- Input validation (422) and not-found errors (404)

## Tech Stack

- Python 3.10+
- FastAPI
- PostgreSQL
- psycopg2 (raw SQL, no ORM)
- python-dotenv
- Uvicorn

## Prerequisites

- Python 3.10 or newer
- PostgreSQL installed and running
- git

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/rintu783/user-management-api.git
cd user-management-api
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the database and table

```bash
sudo -u postgres psql
```

```sql
CREATE USER user_api WITH PASSWORD 'change_me';
CREATE DATABASE user_management OWNER user_api;
\q
```

Then create the table using the provided file:

```bash
psql -h localhost -U user_api -d user_management -f app/schema.sql
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
DB_HOST=localhost
DB_NAME=user_management
DB_USER=user_api
DB_PASSWORD=change_me
```

### 6. Run the app

```bash
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000.

## API Endpoints

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| POST | /users | Create a user | 201 | 422 |
| GET | /users | List all users | 200 | none |
| PUT | /users/{user_id} | Update a user | 200 | 404, 422 |
| DELETE | /users/{user_id} | Delete a user | 204 | 404 |

## User Fields

| Field | Type | Notes |
|---|---|---|
| name | text | |
| gender | text | |
| age | integer | entered manually, not calculated from dob |
| dob | date | format `YYYY-MM-DD`, e.g. `1999-12-05` |
| address | text | |
| blood_group | text | e.g. `O+` |
| time_zone | text | e.g. `Asia/Kolkata` |

## Example Requests and Responses

### Create user: POST /users

Request body:

```json
{
  "name": "Rintu Kurian",
  "gender": "male",
  "age": 26,
  "dob": "1999-12-05",
  "address": "12 MG Road, Kolkata",
  "blood_group": "O+",
  "time_zone": "Asia/Kolkata"
}
```

Response (201):

```json
{
  "id": 1,
  "name": "Rintu Kurian",
  "gender": "male",
  "age": 26,
  "dob": "1999-12-05",
  "address": "12 MG Road, Kolkata",
  "blood_group": "O+",
  "time_zone": "Asia/Kolkata"
}
```

### Not found: PUT or DELETE /users/9999

Response (404):

```json
{ "detail": "User 9999 not found" }
```

### Invalid body: POST /users with `"age": "abc"`

Response (422): a JSON body listing the invalid fields and the reasons.

## Testing with Swagger UI

1. Start the app and open http://127.0.0.1:8000/docs.
2. Click an endpoint, then "Try it out".
3. Fill in the parameters or body and click "Execute".
4. Check the status code and response body.

## Project Structure

```
main.py            # FastAPI app, routes, database helper
schema.sql         # table definition
requirements.txt   # Python dependencies
.env.example       # template for environment variables
```