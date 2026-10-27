"""Tests every endpoint of the running API.

1. Start the app:                 uvicorn app.main:app --reload
2. In another terminal (venv on): python test_endpoints.py

Optional: pass a different address, e.g.  python test_endpoints.py http://127.0.0.1:8001
The script creates one test user and removes it again at the end.
"""
import sys

import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
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

passed = 0
failed = 0


def check(name, condition, response=None):
    """Print PASS or FAIL for one test and keep count."""
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS  {name}")
    else:
        failed += 1
        print(f"FAIL  {name}")
        if response is not None:
            print(f"      got status {response.status_code}: {response.text}")


def has_fields(body, expected):
    """True if every field in expected has the same value in body."""
    for key, value in expected.items():
        if body.get(key) != value:
            return False
    return True


def run_tests():
    # 1. Create a user
    r = requests.post(f"{BASE_URL}/users", json=NEW_USER, timeout=10)
    check("POST /users returns 201", r.status_code == 201, r)
    if r.status_code != 201:
        print("Cannot continue without a created user.")
        return None
    user = r.json()
    user_id = user["id"]
    check("POST /users returns the saved fields and an id", has_fields(user, NEW_USER), r)

    # 2. Invalid body
    bad_user = dict(NEW_USER, age="abc")
    r = requests.post(f"{BASE_URL}/users", json=bad_user, timeout=10)
    check("POST /users with age='abc' returns 422", r.status_code == 422, r)

    missing_field = dict(NEW_USER)
    del missing_field["name"]
    r = requests.post(f"{BASE_URL}/users", json=missing_field, timeout=10)
    check("POST /users without name returns 422", r.status_code == 422, r)

    # 3. List users
    r = requests.get(f"{BASE_URL}/users", timeout=10)
    ids = [u["id"] for u in r.json()] if r.status_code == 200 else []
    check("GET /users returns 200 and includes the new user", r.status_code == 200 and user_id in ids, r)

    # 4. Get one user
    r = requests.get(f"{BASE_URL}/users/{user_id}", timeout=10)
    check("GET /users/{id} returns 200 with the right user",
          r.status_code == 200 and has_fields(r.json(), NEW_USER), r)

    r = requests.get(f"{BASE_URL}/users/{MISSING_ID}", timeout=10)
    check("GET /users/{missing id} returns 404", r.status_code == 404, r)

    r = requests.get(f"{BASE_URL}/users/abc", timeout=10)
    check("GET /users/abc returns 422", r.status_code == 422, r)

    # 5. Update
    r = requests.put(f"{BASE_URL}/users/{user_id}", json=UPDATED_USER, timeout=10)
    check("PUT /users/{id} returns 200 with the new values",
          r.status_code == 200 and has_fields(r.json(), UPDATED_USER), r)

    r = requests.get(f"{BASE_URL}/users/{user_id}", timeout=10)
    check("The update was saved in the database",
          r.status_code == 200 and has_fields(r.json(), UPDATED_USER), r)

    r = requests.put(f"{BASE_URL}/users/{MISSING_ID}", json=UPDATED_USER, timeout=10)
    check("PUT /users/{missing id} returns 404", r.status_code == 404, r)

    # 6. Delete
    r = requests.delete(f"{BASE_URL}/users/{user_id}", timeout=10)
    check("DELETE /users/{id} returns 204 with an empty body",
          r.status_code == 204 and r.text == "", r)

    r = requests.delete(f"{BASE_URL}/users/{user_id}", timeout=10)
    check("DELETE the same id again returns 404", r.status_code == 404, r)

    r = requests.get(f"{BASE_URL}/users/{user_id}", timeout=10)
    check("GET the deleted user returns 404", r.status_code == 404, r)

    return user_id


def main():
    print(f"Testing {BASE_URL}\n")

    try:
        requests.get(f"{BASE_URL}/docs", timeout=5)
    except requests.exceptions.ConnectionError:
        print("Could not connect. Start the app first:  uvicorn app.main:app --reload")
        sys.exit(1)

    user_id = None
    try:
        user_id = run_tests()
    finally:
        # Clean up the test user if a test stopped before the delete step
        if user_id is not None:
            requests.delete(f"{BASE_URL}/users/{user_id}", timeout=10)

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()