
import sqlite3

def check_db():
    conn = sqlite3.connect('coding_platform.db')
    cursor = conn.cursor()
    
    print("--- TestCases Table Columns ---")
    cursor.execute("PRAGMA table_info(testcases);")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
        
    conn.close()

if __name__ == "__main__":
    check_db()
