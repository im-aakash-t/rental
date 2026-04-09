# bill_number.py - ENHANCED VERSION (4-Digit Format)
import re
import logging

logger = logging.getLogger(__name__)

def increment_prefix(prefix: str) -> str:
    """
    Increments an alphabetic bill prefix: 'A' → 'B', ..., 'Z' → 'AA', ..., 'ZZ' → 'AAA'.
    Handles case-insensitivity and empty input robustly.
    """
    if not prefix:
        return "A"
    
    prefix = prefix.upper()
    chars = list(prefix)
    i = len(chars) - 1
    
    while i >= 0:
        if chars[i] != "Z":
            chars[i] = chr(ord(chars[i]) + 1)
            # Reset all characters to the right to 'A'
            chars[i+1:] = ['A'] * (len(chars) - i - 1)
            return ''.join(chars)
        i -= 1
    
    # All characters were 'Z', add new 'A' at beginning
    return "A" * (len(prefix) + 1)

def generate_next_bill_no(db) -> str:
    """
    Scheme: PREFIX + 4-digit number (e.g., 'A0001'). Rolls over after 9999 → next prefix.
    Returns 'A0001' if no bill exists, or if an invalid last bill found.
    """
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        # Get the latest bill number with proper error handling
        cur.execute("""
            SELECT bill_no FROM rentals 
            WHERE bill_no IS NOT NULL AND bill_no != '' 
            ORDER BY id DESC LIMIT 1
        """)
        row = cur.fetchone()
        last = str(row[0]).strip().upper() if row and row[0] else ""
        
        # If no existing bills, start with A0001
        if not last:
            logger.info("No existing bills found, starting with A0001")
            return "A0001"

        # Validate and parse the last bill number (Changed to 4 digits)
        match = re.match(r"^([A-Z]+)(\d{4})$", last)
        if not match:
            logger.warning(f"Invalid bill number format: '{last}', resetting to A0001")
            return "A0001"

        prefix, number_str = match.groups()
        
        try:
            number = int(number_str) + 1
        except ValueError:
            logger.warning(f"Invalid number in bill '{last}', resetting to A0001")
            return "A0001"
        
        # Changed rollover limit to 9999
        if number > 9999:
            prefix = increment_prefix(prefix)
            number = 1
            logger.info(f"Bill number rolled over to new prefix: {prefix}")
        
        # Format with 4 digits instead of 5
        next_bill = f"{prefix}{number:04d}"
        logger.debug(f"Generated next bill number: {next_bill}")
        return next_bill
        
    except Exception as e:
        logger.error(f"Bill number generation failed: {e}")
        # Fallback to ensure we always return a valid bill number
        return "A0001"

def validate_bill_no(bill_no: str) -> bool:
    """
    Validate bill number format.
    """
    if not bill_no or not isinstance(bill_no, str):
        return False
    
    # Changed regex to expect exactly 4 digits
    return bool(re.match(r"^[A-Z]+\d{4}$", bill_no.strip().upper()))

def extract_bill_components(bill_no: str):
    """
    Extract prefix and number from bill number.
    Returns (prefix, number) or (None, None) if invalid.
    """
    if not validate_bill_no(bill_no):
        return None, None
    
    # Changed regex to expect exactly 4 digits
    match = re.match(r"^([A-Z]+)(\d{4})$", bill_no.strip().upper())
    if match:
        return match.groups()
    return None, None