"""
Central registry for callback functions that allow cross-tab UI refresh
and data reloading in a Tkinter application.
"""

# Callback placeholders for use across UI tabs
reload_balance_tab = None
reload_pending_materials_tab = None
reload_customer_report_tab = None
pending_reload_table = None
customer_report_reload_table = None

def register_tab_callbacks(balance_cb=None, materials_cb=None, customer_cb=None):
    """
    Register callbacks for tab reloads.
    
    Args:
        balance_cb: function to reload balance tab
        materials_cb: function to reload pending/materials tab  
        customer_cb: function to reload customer report tab
    """
    global reload_balance_tab, reload_pending_materials_tab, reload_customer_report_tab
    reload_balance_tab = balance_cb
    reload_pending_materials_tab = materials_cb
    reload_customer_report_tab = customer_cb

def reload_all_tabs():
    """
    Trigger all reload functions currently registered.
    Useful to refresh every tab after database/state changes.
    """
    callbacks = [
        reload_balance_tab,
        reload_pending_materials_tab, 
        reload_customer_report_tab,
        pending_reload_table,
        customer_report_reload_table
    ]
    
    for callback in callbacks:
        if callback:
            callback()