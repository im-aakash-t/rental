import sqlite3

def get_db_structure(db_path):
    print(f"\n{'='*40}")
    print(f"--- STRUCTURE FOR: {db_path} ---")
    print(f"{'='*40}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("⚠️ No tables found in this database!")
            return

        for table in tables:
            table_name = table[0]
            
            # Skip SQLite's internal background tables
            if table_name.startswith('sqlite_'):
                continue
                
            print(f"\nTable: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                # col[1] is the column name, col[2] is the data type
                print(f"  - {col[1]} ({col[2]})")
                
        conn.close()
        print("\n" + "="*40 + "\n")
        
    except sqlite3.Error as e:
        print(f"❌ Error reading database {db_path}: {e}")

if __name__ == "__main__":
    # ---> CHANGE THIS FILENAME TO TEST DIFFERENT DATABASES <---
    
    # Example 1: Run it for the old database
    get_db_structure("rentals.db") 
    
    # Example 2: Run it for the new database
    # get_db_structure("new_rentals.db")