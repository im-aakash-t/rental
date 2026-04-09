# import_helper.py - NEW FILE for safe imports
"""
Helper functions for safe importing to avoid circular dependencies.
"""

import importlib
import sys
from shared_imports import log_error

def safe_import(module_name, attribute_name=None):
    """
    Safely import a module or attribute with error handling.
    """
    try:
        module = importlib.import_module(module_name)
        if attribute_name:
            return getattr(module, attribute_name)
        return module
    except ImportError as e:
        log_error(f"Import {module_name}.{attribute_name}", e)
        raise
    except AttributeError as e:
        log_error(f"Attribute {attribute_name} in {module_name}", e)
        raise

def get_tab_creator(tab_name):
    """
    Get tab creation function safely.
    """
    tab_modules = {
        'form': ('form_tab', 'create_form_tab'),
        'partial_returns': ('partial_returns_tab', 'create_partial_returns_tab'),
        'pending': ('pending_tab', 'create_pending_tab'),
        'customer_report': ('customer_report_tab', 'create_customer_report_tab'),
        'analytics': ('analytics_dashboard', 'create_analytics_tab')
    }
    
    if tab_name in tab_modules:
        module_name, function_name = tab_modules[tab_name]
        return safe_import(module_name, function_name)
    
    raise ValueError(f"Unknown tab: {tab_name}")

# Pre-loaded tab creators for performance
_tab_creators = {}

def preload_tab_creators():
    """Preload all tab creators to avoid runtime delays."""
    global _tab_creators
    tab_names = ['form', 'partial_returns', 'pending', 'customer_report', 'analytics']
    
    for tab_name in tab_names:
        try:
            _tab_creators[tab_name] = get_tab_creator(tab_name)
        except Exception as e:
            log_error(f"Preloading tab {tab_name}", e)
            _tab_creators[tab_name] = None

def create_tab(tab_name, tab_control, db, **kwargs):
    """Create a tab using pre-loaded creator."""
    if tab_name not in _tab_creators:
        preload_tab_creators()
    
    creator = _tab_creators.get(tab_name)
    if not creator:
        raise ValueError(f"Tab creator for {tab_name} not available")
    
    return creator(tab_control, db, **kwargs)