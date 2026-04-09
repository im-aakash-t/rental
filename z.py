import sqlite3
import shutil
import os

OLD_DB = "old_rentals.db"
NEW_DB = "rentals.db"

def migrate_database():
    print(f"🚀 Starting Database Migration: {OLD_DB} -> {NEW_DB}")
    
    if not os.path.exists(OLD_DB):
        print(f"❌ ERROR: Could not find '{OLD_DB}'. Please make sure the file is in this folder.")
        return

    # Create a fresh copy of the old DB to work on, so we don't destroy the original
    if os.path.exists(NEW_DB):
        print(f"⚠️ '{NEW_DB}' already exists. Overwriting it with migration data...")
    shutil.copy2(OLD_DB, NEW_DB)
    
    conn = sqlite3.connect(NEW_DB)
    c = conn.cursor()

    try:
        # ---------------------------------------------------------
        # 1. RENAME 'amount_returned' TO 'refund' IN 'returns' TABLE
        # ---------------------------------------------------------
        c.execute("PRAGMA table_info(returns)")
        returns_cols = [col[1] for col in c.fetchall()]
        
        if 'amount_returned' in returns_cols and 'refund' not in returns_cols:
            c.execute("ALTER TABLE returns RENAME COLUMN amount_returned TO refund")
            print("✅ Renamed 'amount_returned' to 'refund' in returns table.")
        elif 'refund' in returns_cols:
            print("✅ 'refund' column already exists in returns table.")

        # ---------------------------------------------------------
        # 2. MIGRATE 'payments' TO 'installments'
        # ---------------------------------------------------------
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
        if c.fetchone():
            print("🔄 Migrating 'payments' table to 'installments'...")
            
            # Create the new installments table
            c.execute("""
                CREATE TABLE IF NOT EXISTS installments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rental_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_mode TEXT,
                    cashier_name TEXT,
                    date_time TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Move the data, combining payment_date and payment_time into date_time
            c.execute("""
                INSERT INTO installments (rental_id, amount, payment_mode, cashier_name, date_time)
                SELECT 
                    rental_id, 
                    amount, 
                    payment_mode, 
                    cashier_name, 
                    payment_date || ' ' || payment_time 
                FROM payments
            """)
            
            # Drop the old payments table
            c.execute("DROP TABLE payments")
            print("✅ 'payments' successfully converted to 'installments'.")
        else:
            print("ℹ️ No 'payments' table found. Checking if 'installments' already exists.")
            c.execute("""
                CREATE TABLE IF NOT EXISTS installments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rental_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_mode TEXT,
                    cashier_name TEXT,
                    date_time TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # ---------------------------------------------------------
        # 3. CREATE AND POPULATE 'customers' (CRM)
        # ---------------------------------------------------------
        c.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                phone2 TEXT,
                address TEXT,
                is_regular INTEGER DEFAULT 0
            )
        ''')
        
        # Populate from existing rentals
        c.execute('''
            INSERT OR IGNORE INTO customers (name, phone, phone2, address)
            SELECT name, phone, phone2, address 
            FROM rentals 
            WHERE phone IS NOT NULL AND phone != '' 
            GROUP BY phone
        ''')
        print("✅ 'customers' table created and populated with past data.")

        conn.commit()
        print("\n🎉 MIGRATION COMPLETE! Your new 'rentals.db' is ready to use in V2.")

    except Exception as e:
        conn.rollback()
        print(f"❌ CRITICAL ERROR DURING MIGRATION: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()