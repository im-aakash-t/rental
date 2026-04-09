# modern_theme.py - REFINED VERSION (More compact UI elements)
from tkinter import ttk
import tkinter as tk

def set_modern_theme(root):
    """Sets a modern UI theme for Tkinter widgets without conflicts."""
    
    style = ttk.Style(root)
    available_themes = style.theme_names()
    preferred_themes = ['vista', 'xpnative', 'clam', 'alt', 'default']
    
    for theme in preferred_themes:
        if theme in available_themes:
            try:
                style.theme_use(theme)
                break
            except:
                continue
    else:
        style.theme_use(available_themes[0] if available_themes else 'clam')

    colors = {
        'primary': '#2176ff', 'primary_dark': '#1a5fd8', 'primary_darker': '#1554c4',
        'secondary': '#4CAF50', 'secondary_dark': '#45a049',
        'warning': '#ff9800', 'danger': '#f44336', 'danger_dark': '#da190b',
        'background': '#f8f9fa', 'surface': '#ffffff',
        'text_primary': '#212529', 'text_secondary': '#6c757d',
        'border': '#dee2e6'
    }

    style.configure('.', background=colors['background'], foreground=colors['text_primary'], font=('Segoe UI', 10))

    style.configure('TFrame', background=colors['background'])
    style.configure('Card.TFrame', background=colors['surface'], relief='solid', borderwidth=1)

    style.configure('TLabel', background=colors['background'], font=('Segoe UI', 10))
    style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), foreground=colors['primary'])
    style.configure('Subtitle.TLabel', font=('Segoe UI', 11, 'bold'), foreground=colors['text_secondary'])

    button_config = {
        'font': ('Segoe UI', 10, 'bold'), 'padding': (12, 5), 'borderwidth': 1,
        'focusthickness': 1, 'focuscolor': colors['primary']
    }
    style.configure('TButton', **button_config)
    style.configure('Primary.TButton', background=colors['primary'], foreground='white')
    style.configure('Success.TButton', background=colors['secondary'], foreground='white')
    style.configure('Danger.TButton', background=colors['danger'], foreground='white')

    style.map('TButton',
             background=[('active', colors['primary']), ('pressed', colors['primary_dark'])],
             foreground=[('active', 'white'), ('pressed', 'white')])

    entry_config = {
        'font': ('Segoe UI', 10), 'padding': (6, 4), 'relief': 'solid',
        'borderwidth': 1, 'focusthickness': 1, 'focuscolor': colors['primary']
    }
    
    style.configure('TEntry', **entry_config)
    style.configure('TCombobox', **entry_config)
    style.map('TEntry', fieldbackground=[('disabled', '#f5f5f5')], foreground=[('disabled', colors['text_secondary'])])

    style.configure('TLabelframe', background=colors['background'], relief='solid', borderwidth=1, padding=8)
    style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground=colors['primary'], background=colors['background'])

    style.configure('TNotebook', background=colors['background'], borderwidth=0)
    style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=(15, 6), background='#e9ecef', foreground=colors['text_secondary'], borderwidth=1)
    style.map('TNotebook.Tab',
             background=[('selected', colors['surface']), ('active', colors['primary'])],
             foreground=[('selected', colors['primary']), ('active', 'white')])

    # COMPACTED ROW HEIGHT TO FIT MORE DATA
    style.configure('Treeview', font=('Segoe UI', 10), rowheight=25, background=colors['surface'], fieldbackground=colors['surface'], borderwidth=0)
    style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background='#e9ecef', foreground=colors['text_primary'], padding=(10, 5), relief='flat')
    style.map('Treeview.Heading', background=[('active', '#dee2e6')])

    scrollbar_config = {'background': colors['background'], 'troughcolor': colors['background'], 'borderwidth': 0, 'relief': 'flat'}
    style.configure('Vertical.TScrollbar', **scrollbar_config)
    style.configure('Horizontal.TScrollbar', **scrollbar_config)

    try:
        root.configure(background=colors['background'])
        root.option_add('*TEntry*background', colors['surface'])
        root.option_add('*TEntry*foreground', colors['text_primary'])
        root.option_add('*Text*background', colors['surface'])
        root.option_add('*Text*foreground', colors['text_primary'])
        root.option_add('*Listbox*background', colors['surface'])
        root.option_add('*Listbox*foreground', colors['text_primary'])
    except Exception as e:
        print(f"[THEME] Minor configuration issue: {e}")

def create_tooltip(widget, text, delay=1000):
    """Create an enhanced tooltip for widgets with better positioning."""
    import tkinter as tk
    
    def show_tooltip(event):
        if hasattr(widget, '_tooltip'):
            widget._tooltip.destroy()
        
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True) # Only called once now
        
        x = event.x_root + 15
        y = event.y_root + 10
        
        screen_width = widget.winfo_screenwidth()
        screen_height = widget.winfo_screenheight()
        
        if x + 200 > screen_width: x = screen_width - 220
        if y + 60 > screen_height: y = event.y_root - 70
        
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tooltip, text=text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=('Segoe UI', 9), padx=8, pady=4)
        label.pack()
        widget._tooltip = tooltip
        
    def hide_tooltip(event):
        if hasattr(widget, '_tooltip'):
            widget._tooltip.destroy()
            delattr(widget, '_tooltip')
            
    widget.bind("<Enter>", lambda e: widget.after(delay, show_tooltip, e))
    widget.bind("<Leave>", lambda e: widget.after(100, hide_tooltip, e))
    widget.bind("<Motion>", hide_tooltip)