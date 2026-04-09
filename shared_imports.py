# shared_imports.py - REFINED VERSION
from db_manager import DBManager

from utils import (
    safe_float, safe_int, sync_lists, validate_phone, validate_date, 
    validate_time, format_currency, sanitize_sql_input,
    calculate_rental_total, calculate_balance, validate_machine_data, log_error,
    calculate_rental_days_unified
)

from billing import (
    validate_form, save_form_data, update_form_data, load_all_records,
    get_record_by_id, has_return_entry, has_pending_returns, cancel_rental,
    BillingError, calculate_due_amount, print_bill_from_record, get_customer_credit
)

from bill_number import generate_next_bill_no, validate_bill_no
from materials import load_materials, get_material_by_code

import callbacks
from analytics_dashboard import AnalyticsDashboard, create_analytics_tab

from return_logic import (
    get_full_rental_details, save_return_data, generate_return_pdf,
    should_freeze_return_fields, calculate_rental_days, get_customer_history
)

from export_manager import ExportManager
from backup_manager import BackupManager
from drive_backup import backup_files
from modern_theme import set_modern_theme, create_tooltip

def calculate_master_balance(daily_rent, rental_days, advance_paid, installments_paid=0.0, 
                             damage_charges=0.0, discount_deduction=0.0, 
                             final_amount_paid=0.0, refund_given=0.0, 
                             is_returned=False, manual_due_override=None):
    """
    THE ONE TRUE MATH ENGINE 🚀
    Every single balance calculation in the software goes through here.
    """
    try:
        from utils import safe_float, safe_int
    except:
        def safe_float(val):
            try: return float(val)
            except: return 0.0
        def safe_int(val):
            try: return int(float(val))
            except: return 0

    # 1. Clean all inputs
    rent = safe_float(daily_rent)
    days = max(1, safe_int(rental_days)) 
    adv = safe_float(advance_paid)
    inst = safe_float(installments_paid)
    dmg = safe_float(damage_charges)
    deduct = safe_float(discount_deduction)
    paid = safe_float(final_amount_paid)
    ref = safe_float(refund_given)

    # 2. Total Rent Cost (Respect manual overrides if the user edited the Due field)
    if manual_due_override is not None and str(manual_due_override).strip() != "":
        due_amount = safe_float(manual_due_override)
    else:
        due_amount = rent * days

    # 3. Prevent Double Counting (Use whichever is higher: live installments vs final paid input)
    total_paid_so_far = max(inst, paid)

    # 4. Apply Business Logic
    if is_returned:
        net_balance = (due_amount + dmg) - (adv + total_paid_so_far + deduct) + ref
    else:
        net_balance = due_amount - (adv + total_paid_so_far)

    return due_amount, net_balance

__all__ = [
    'DBManager', 'safe_float', 'safe_int', 'sync_lists', 'validate_phone', 'validate_date', 
    'validate_time', 'format_currency', 'sanitize_sql_input', 'calculate_rental_total',
    'calculate_balance', 'validate_machine_data', 'log_error', 'calculate_rental_days_unified',
    'validate_form', 'save_form_data', 'update_form_data', 'load_all_records',
    'get_record_by_id', 'has_return_entry', 'has_pending_returns', 'cancel_rental',
    'BillingError', 'calculate_due_amount', 'print_bill_from_record', 'get_customer_credit',
    'generate_next_bill_no', 'validate_bill_no', 'load_materials', 'get_material_by_code',
    'callbacks', 'AnalyticsDashboard', 'create_analytics_tab', 'get_full_rental_details', 
    'save_return_data', 'generate_return_pdf', 'should_freeze_return_fields', 
    'calculate_rental_days', 'get_customer_history', 'ExportManager',
    'BackupManager', 'backup_files', 'set_modern_theme', 'create_tooltip',
    'calculate_master_balance'
]