import sqlite3

def check_db():
    conn = sqlite3.connect('coding_platform.db')
    cursor = conn.cursor()
    
    print("\n--- All Users ---")
    cursor.execute("SELECT id, name, role FROM users")
    for row in cursor.fetchall():
        print(row)
            
    conn.close()

if __name__ == "__main__":
    check_db()
