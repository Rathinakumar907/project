import sqlite3
import json

def get_users():
    conn = sqlite3.connect('coding_platform.db')
    cursor = conn.cursor()
    query = "SELECT id, name, email, university_id, password_hash, role FROM users;"
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    try:
        users = get_users()
        with open('users_data.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error: {e}")
