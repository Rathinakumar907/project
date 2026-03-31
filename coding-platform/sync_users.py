import json
import sqlite3
import os

def sync_users():
    json_path = "users_data.json"
    db_path = "coding_platform.db"

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r") as f:
        users = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Syncing {len(users)} users from JSON to database...")

    for user in users:
        # Check if user already exists in DB
        cursor.execute("SELECT id FROM users WHERE email = ?", (user['email'],))
        row = cursor.fetchone()

        if row:
            # Update existing user
            cursor.execute("""
                UPDATE users 
                SET name = ?, university_id = ?, password_hash = ?, role = ?
                WHERE email = ?
            """, (user['name'], user['university_id'], user['password_hash'], user['role'], user['email']))
        else:
            # Insert new user
            cursor.execute("""
                INSERT INTO users (name, email, university_id, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
            """, (user['name'], user['email'], user['university_id'], user['password_hash'], user['role']))

    conn.commit()
    conn.close()
    print("User synchronization complete.")

if __name__ == "__main__":
    sync_users()
