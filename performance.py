# performance.py - NEW FILE for performance optimizations
"""
Performance optimization utilities for handling large datasets.
"""

import sqlite3
from functools import lru_cache
import threading
from shared_imports import log_error

class QueryOptimizer:
    """Optimize database queries for better performance."""
    
    def __init__(self, db):
        self.db = db
        self._cache = {}
        self._lock = threading.RLock()
    
    @lru_cache(maxsize=100)
    def get_customer_balance(self, phone):
        """Cached customer balance calculation."""
        try:
            conn = self.db.get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT COALESCE(SUM(balance), 0) FROM returns
                WHERE rental_id IN (
                    SELECT id FROM rentals WHERE phone = ?
                )
            """, (phone,))
            return c.fetchone()[0] or 0
        except Exception as e:
            log_error(f"Customer balance for {phone}", e)
            return 0
    
    def batch_load_records(self, limit=1000, offset=0, filters=None):
        """Load records in batches for better memory management."""
        try:
            conn = self.db.get_connection()
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            query = """
                SELECT id, bill_no, name, phone, address, date, total, advance, 
                       machines, quantities, rents, cancelled
                FROM rentals 
                WHERE 1=1
            """
            params = []
            
            if filters:
                if filters.get('search'):
                    query += " AND (name LIKE ? OR phone LIKE ? OR bill_no LIKE ?)"
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term, search_term])
                
                if filters.get('cancelled') is not None:
                    query += " AND cancelled = ?"
                    params.append(filters['cancelled'])
            
            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            c.execute(query, params)
            return [dict(row) for row in c.fetchall()]
            
        except Exception as e:
            log_error("Batch record loading", e)
            return []
    
    def clear_cache(self):
        """Clear the query cache."""
        with self._lock:
            self._cache.clear()
        self.get_customer_balance.cache_clear()

class MemoryManager:
    """Manage memory usage for large datasets."""
    
    @staticmethod
    def chunked_process(iterable, chunk_size=1000, process_func=None):
        """Process large datasets in chunks to avoid memory issues."""
        results = []
        chunk = []
        
        for item in iterable:
            chunk.append(item)
            if len(chunk) >= chunk_size:
                if process_func:
                    results.extend(process_func(chunk))
                else:
                    results.extend(chunk)
                chunk = []
        
        # Process remaining items
        if chunk:
            if process_func:
                results.extend(process_func(chunk))
            else:
                results.extend(chunk)
        
        return results
    
    @staticmethod
    def estimate_memory_usage(obj):
        """Estimate memory usage of an object (rough estimate)."""
        import sys
        return sys.getsizeof(obj)

def create_indexed_view(db, view_name, query):
    """Create an indexed view for frequently accessed data."""
    try:
        conn = db.get_connection()
        c = conn.cursor()
        
        # Drop existing view
        c.execute(f"DROP VIEW IF EXISTS {view_name}")
        
        # Create new view
        c.execute(f"CREATE VIEW IF NOT EXISTS {view_name} AS {query}")
        conn.commit()
        
        log_error(f"View {view_name} created", "Success", level='INFO')
        return True
        
    except Exception as e:
        log_error(f"View creation {view_name}", e)
        return False

# Create performance-optimized views
CUSTOMER_SUMMARY_VIEW = """
CREATE VIEW IF NOT EXISTS customer_summary AS
SELECT 
    phone,
    name,
    COUNT(*) as rental_count,
    SUM(total) as total_billed,
    SUM(advance) as total_advance,
    (SELECT COALESCE(SUM(balance), 0) FROM returns 
     WHERE rental_id IN (SELECT id FROM rentals r2 WHERE r2.phone = r.phone)) as total_balance
FROM rentals r
WHERE cancelled = 0 OR cancelled IS NULL
GROUP BY phone, name
"""

PENDING_RETURNS_VIEW = """
CREATE VIEW IF NOT EXISTS pending_returns_view AS
SELECT 
    r.id,
    r.bill_no,
    r.name,
    r.phone,
    r.machines,
    r.quantities,
    COALESCE(ret.returned_items, '') as returned_items,
    COALESCE(ret.returned_quantities, '') as returned_quantities,
    (r.total - r.advance) as pending_amount
FROM rentals r
LEFT JOIN returns ret ON r.id = ret.rental_id
WHERE (r.cancelled = 0 OR r.cancelled IS NULL)
AND (ret.returned_items IS NULL OR ret.returned_items != r.machines)
"""