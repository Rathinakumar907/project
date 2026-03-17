import sqlite3

db_path = "coding_platform.db"

def populate():
    subjects = [
        "Python",
        "Data Structures and Algorithms (DSA)",
        "Python and DSA Lab"
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for s in subjects:
        try:
            cursor.execute("INSERT INTO subjects (subject_name) VALUES (?)", (s,))
            print(f"Added subject: {s}")
        except sqlite3.IntegrityError:
            print(f"Subject '{s}' already exists.")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate()
