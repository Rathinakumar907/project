import sqlite3
import os

db_path = "coding_platform.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Column migrations (ALTER TABLE)
    migrations = [
        ("problems", "reference_solution", "ALTER TABLE problems ADD COLUMN reference_solution TEXT;"),
        ("submissions", "score", "ALTER TABLE submissions ADD COLUMN score INTEGER DEFAULT 0;"),
        ("submissions", "status", "ALTER TABLE submissions ADD COLUMN status TEXT;"),
        ("submissions", "passed_testcases", "ALTER TABLE submissions ADD COLUMN passed_testcases INTEGER DEFAULT 0;"),
        ("submissions", "total_testcases", "ALTER TABLE submissions ADD COLUMN total_testcases INTEGER DEFAULT 0;"),
        ("problems", "total_marks", "ALTER TABLE problems ADD COLUMN total_marks INTEGER DEFAULT 100;"),
        ("submissions", "exam_session_id", "ALTER TABLE submissions ADD COLUMN exam_session_id INTEGER;"),
        ("testcases", "marks_weight", "ALTER TABLE testcases ADD COLUMN marks_weight INTEGER DEFAULT 1;"),
        ("problems", "subject_id", "ALTER TABLE problems ADD COLUMN subject_id INTEGER;"),
    ]

    for table, column, sql in migrations:
        try:
            print(f"Checking '{column}' in '{table}'...")
            cursor.execute(sql)
            print(f"  ✓ Added '{column}' column.")
        except sqlite3.OperationalError:
            print(f"  - Column '{column}' already exists.")

    # Table migrations (CREATE TABLE)
    new_tables = {
        "exam_sessions": """
            CREATE TABLE IF NOT EXISTS exam_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                problem_id INTEGER,
                session_token TEXT UNIQUE,
                start_time DATETIME,
                end_time DATETIME,
                status TEXT DEFAULT 'active',
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(problem_id) REFERENCES problems(id)
            );
        """,
        "violations": """
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                event_type TEXT,
                timestamp DATETIME,
                metadata_json TEXT,
                FOREIGN KEY(session_id) REFERENCES exam_sessions(id)
            );
        """,
        "behavior_logs": """
            CREATE TABLE IF NOT EXISTS behavior_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp DATETIME,
                typing_speed INTEGER,
                paste_count INTEGER DEFAULT 0,
                paste_size INTEGER DEFAULT 0,
                idle_time INTEGER DEFAULT 0,
                FOREIGN KEY(session_id) REFERENCES exam_sessions(id)
            );
        """,
        "plagiarism_flags": """
            CREATE TABLE IF NOT EXISTS plagiarism_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_1_id INTEGER,
                submission_2_id INTEGER,
                total_similarity INTEGER,
                token_similarity INTEGER,
                ast_similarity INTEGER,
                control_flow_similarity INTEGER,
                timestamp DATETIME,
                status TEXT DEFAULT 'potential',
                FOREIGN KEY(submission_1_id) REFERENCES submissions(id),
                FOREIGN KEY(submission_2_id) REFERENCES submissions(id)
            );
        """,
        "subjects": """
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT UNIQUE
            );
        """,
        "user_subjects": """
            CREATE TABLE IF NOT EXISTS user_subjects (
                user_id INTEGER,
                subject_id INTEGER,
                PRIMARY KEY (user_id, subject_id),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            );
        """
    }

    for table_name, create_sql in new_tables.items():
        try:
            print(f"Creating table '{table_name}' if not exists...")
            cursor.execute(create_sql)
            print(f"  ✓ Success.")
        except Exception as e:
            print(f"  - Error creating table '{table_name}': {e}")

    conn.commit()
    conn.close()
    print("\nMigration complete.")

if __name__ == "__main__":
    migrate()
