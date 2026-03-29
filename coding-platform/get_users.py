import sqlite3

def get_users():
    conn = sqlite3.connect('coding_platform.db')
    cursor = conn.cursor()
    query = "SELECT id, name, email, university_id, password_hash, role FROM users;"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    try:
        users = get_users()
        if not users:
            print("No users found in the database.")
        else:
            print(f"{'ID':<5} | {'Name':<20} | {'Email':<30} | {'Univ ID':<15} | {'Role':<10} | {'Password Hash':<50}")
            print("-" * 140)
            for row in users:
                id, name, email, univ_id, pw_hash, role = row
                print(f"{id:<5} | {name:<20} | {email:<30} | {univ_id:<15} | {role:<10} | {pw_hash[:50]}...")
    except Exception as e:
        print(f"Error querying database: {e}")
