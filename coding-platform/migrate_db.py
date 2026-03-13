import sqlite3
import os

db_path = "coding_platform.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    migrations = [
        # Existing migrations
        ("problems", "reference_solution", "ALTER TABLE problems ADD COLUMN reference_solution TEXT;"),
        ("submissions", "score", "ALTER TABLE submissions ADD COLUMN score INTEGER DEFAULT 0;"),
        # New columns for marks storage system
        ("submissions", "status", "ALTER TABLE submissions ADD COLUMN status TEXT;"),
        ("submissions", "passed_testcases", "ALTER TABLE submissions ADD COLUMN passed_testcases INTEGER DEFAULT 0;"),
        ("submissions", "total_testcases", "ALTER TABLE submissions ADD COLUMN total_testcases INTEGER DEFAULT 0;"),
    ]

    for table, column, sql in migrations:
        try:
            print(f"Adding '{column}' column to '{table}' table...")
            cursor.execute(sql)
            print(f"  ✓ Success.")
        except sqlite3.OperationalError as e:
            print(f"  - Skipped ({e})")

    conn.commit()
    conn.close()
    print("\nMigration complete.")

if __name__ == "__main__":
    migrate()
