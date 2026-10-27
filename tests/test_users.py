"""Endpoint tests using FastAPI's TestClient.

Run from the project root (venv active):   python -m pytest -v

The tests use the real database from your .env. Besides checking the API
responses, they also query the database directly (with run_query) to confirm
that rows were really created, changed or removed.
Each test cleans up the users it creates.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app, run_query

client = TestClient(app)

MISSING_ID = 999999

NEW_USER = {
    "name": "Test User",
    "gender": "male",
    "age": 26,
    "dob": "1999-12-05",
    "address": "12 MG Road, Kolkata",
    "blood_group": "O+",
    "time_zone": "Asia/Kolkata",
}

UPDATED_USER = dict(NEW_USER, age=27, address="45 Park Street, Kochi")


# ---------- Helpers ----------
def assert_fields(body, expected):
    """Check that every field in expected has the same value in body."""
    for key, value in expected.items():
        assert body[key] == value, f"{key}: expected {value!r}, got {body[key]!r}"


def get_row(user_id):
    """Read one user straight from the database (not through the API)."""
    row = run_query("SELECT * FROM users WHERE id = %s", (user_id,), "one")
    if row is not None:
        row["dob"] = str(row["dob"])  # the database returns a date object
    return row


def count_users():
    """Count the rows in the users table straight from the database."""
    row = run_query("SELECT COUNT(*) AS total FROM users", fetch="one")
    return row["total"]


@pytest.fixture
def created_user():
    """Create a user before the test, hand it to the test, delete it afterwards."""
    response = client.post("/users", json=NEW_USER)
    assert response.status_code == 201
    user = response.json()
    yield user
    client.delete(f"/users/{user['id']}")  # harmless 404 if the test already deleted it


# ---------- Create ----------
def test_create_user_returns_201_and_saves_row_in_database():
    before = count_users()
    response = client.post("/users", json=NEW_USER)
    try:
        assert response.status_code == 201
        body = response.json()
        assert "id" in body
        assert_fields(body, NEW_USER)

        # check the database directly
        assert count_users() == before + 1
        row = get_row(body["id"])
        assert row is not None, "row was not found in the database"
        assert_fields(row, NEW_USER)
    finally:
        if response.status_code == 201:
            client.delete(f"/users/{response.json()['id']}")


def test_create_user_with_text_age_returns_422_and_saves_nothing():
    before = count_users()
    response = client.post("/users", json=dict(NEW_USER, age="abc"))
    assert response.status_code == 422
    assert count_users() == before


def test_create_user_without_name_returns_422_and_saves_nothing():
    before = count_users()
    body = dict(NEW_USER)
    del body["name"]
    response = client.post("/users", json=body)
    assert response.status_code == 422
    assert count_users() == before


# ---------- Read ----------
def test_list_users_includes_new_user(created_user):
    response = client.get("/users")
    assert response.status_code == 200
    ids = []
    for user in response.json():
        ids.append(user["id"])
    assert created_user["id"] in ids


def test_get_user_returns_the_right_user(created_user):
    response = client.get(f"/users/{created_user['id']}")
    assert response.status_code == 200
    assert_fields(response.json(), NEW_USER)


def test_get_missing_user_returns_404():
    response = client.get(f"/users/{MISSING_ID}")
    assert response.status_code == 404


def test_get_user_with_text_id_returns_422():
    response = client.get("/users/abc")
    assert response.status_code == 422


# ---------- Update ----------
def test_update_user_returns_new_values_and_changes_the_database_row(created_user):
    user_id = created_user["id"]

    response = client.put(f"/users/{user_id}", json=UPDATED_USER)
    assert response.status_code == 200
    assert_fields(response.json(), UPDATED_USER)

    # check the database directly
    row = get_row(user_id)
    assert row is not None
    assert_fields(row, UPDATED_USER)


def test_update_missing_user_returns_404():
    response = client.put(f"/users/{MISSING_ID}", json=UPDATED_USER)
    assert response.status_code == 404


# ---------- Delete ----------
def test_delete_user_returns_204_and_removes_the_database_row(created_user):
    user_id = created_user["id"]
    assert get_row(user_id) is not None  # it exists before the delete

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    assert response.text == ""

    # check the database directly
    assert get_row(user_id) is None, "row is still in the database"


def test_deleted_user_is_gone(created_user):
    user_id = created_user["id"]
    client.delete(f"/users/{user_id}")

    assert client.delete(f"/users/{user_id}").status_code == 404
    assert client.get(f"/users/{user_id}").status_code == 404


def test_delete_missing_user_returns_404():
    response = client.delete(f"/users/{MISSING_ID}")
    assert response.status_code == 404