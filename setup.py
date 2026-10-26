"""Database setup: asks for details, writes .env, creates the user, database and table.

Run from the project root:  python setup_db.py
"""
import os
import re
import subprocess
from getpass import getpass

import psycopg2

SCHEMA_FILE = "schema.sql" if os.path.exists("schema.sql") else "app/schema.sql"


def ask(question, default):
    answer = input(f"{question} [{default}]: ").strip()
    return answer or default


def ask_name(question, default):
    name = ask(question, default)
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise SystemExit(f"'{name}' is not valid. Use letters, numbers and underscores only.")
    return name


def postgres(sql):
    """Run one SQL command as the postgres admin user and return its output."""
    result = subprocess.run(
        ["sudo", "-u", "postgres", "psql", "-tAc", sql],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip())
    return result.stdout.strip()


def main():
    if os.path.exists(".env") and input(".env already exists. Overwrite? (y/n): ").lower() != "y":
        raise SystemExit("Cancelled.")

    db_name = ask_name("Database name", "user_management")
    db_user = ask_name("Database user", "user_api")
    password = getpass("Password for the database user: ")
    if not password or re.search(r"[\s'\"#\\]", password):
        raise SystemExit("Password cannot be empty or contain spaces, quotes, # or backslashes.")

    # 1. Write .env
    with open(".env", "w") as f:
        f.write(f"DB_HOST=localhost\nDB_NAME={db_name}\nDB_USER={db_user}\nDB_PASSWORD={password}\n")
    print(".env created.")

    # 2. Create the user
    if postgres(f"SELECT 1 FROM pg_roles WHERE rolname='{db_user}'"):
        print(f"User '{db_user}' already exists (password unchanged).")
    else:
        postgres(f"CREATE USER {db_user} WITH PASSWORD '{password}'")
        print(f"User '{db_user}' created.")

    # 3. Create the database
    if postgres(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"):
        print(f"Database '{db_name}' already exists.")
    else:
        postgres(f"CREATE DATABASE {db_name} OWNER {db_user}")
        print(f"Database '{db_name}' created.")

    # 4. Create the table
    conn = psycopg2.connect(host="localhost", dbname=db_name, user=db_user, password=password)
    cur = conn.cursor()
    try:
        cur.execute(open(SCHEMA_FILE).read())
        conn.commit()
        print("Table 'users' created.")
    except psycopg2.errors.DuplicateTable:
        print("Table 'users' already exists.")
    finally:
        cur.close()
        conn.close()

    print("Setup complete. Start the app with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()