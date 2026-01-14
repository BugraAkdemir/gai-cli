"""
Centralized UI styling for gai-cli.
Provides a consistent, premium look and feel using Rich.
"""

from rich.console import Console
from rich.theme import Theme
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.style import Style
from rich.padding import Padding
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Confirm
from rich import box
from rich.syntax import Syntax

from gai import config, languages, themes

# Dynamic Console Initialization
def get_console() -> Console:
    """Get a console instance with the current theme."""
    theme_name = config.get_theme()
    theme_def = themes.get_theme(theme_name)
    
    # Map friendly names to style strings
    rich_theme = Theme({
        "info": theme_def["info"],
        "success": theme_def["success"],
        "warning": "yellow",
        "error": theme_def["error"],
        "user": theme_def["user"],
        "ai": theme_def["ai"],
        "border": theme_def["border"],
        "accent": theme_def["accent"],
        "header": theme_def["header"],
        "action.create": "green",
        "action.write": "yellow",
        "action.replace": "yellow",
        "action.append": "blue",
    })
    
    return Console(theme=rich_theme)

console = get_console()

def reload_ui():
    """Reload console theme."""
    global console
    console = get_console()

def translate(key: str) -> str:
    """Get localized string."""
    lang = config.get_language()
    return languages.get_string(key, lang)

# Shortcut
t = translate

def print_header():
    """Print the application header."""
    header_text = translate("header_title")
    # Claude-style: Very subtle, generous whitespace
    console.print()
    console.print(f"[header]  {header_text}  [/header]", justify="center")
    console.print()

def print_welcome():
    """Print a welcome message for first-time users."""
    print_header()
    console.print(f"[info]{translate('welcome')}[/info]", justify="center")
    console.print(f"[accent]{translate('api_key_check')}[/accent]\n", justify="center")

def print_error(message: str):
    """Print a styled error message."""
    # Minimal: 2 space indent, error color
    console.print(f"  [error]✖ {message}[/error]")

def print_success(message: str):
    """Print a styled success message."""
    # Minimal: 2 space indent, success color
    console.print(f"  [success]✔ {message}[/success]")

def print_system(message: str):
    """Print a muted system message."""
    # Minimal: 2 space indent, accent color, subtle arrow
    console.print(f"  [accent]› {message}[/accent]")

def print_plan(plan: dict):
    """Display the proposed agent plan."""
    console.print()
    if plan.get("reasoning"):
        console.print(Padding(f"[info]Reasoning: {plan.get('reasoning')}[/info]", (0, 0, 1, 2)))
        
    console.print(f"  [ai]{translate('plan_title')}[/ai] {plan.get('plan', 'No description')}")
    
    # Minimal clean table
    table = Table(show_header=True, header_style="accent", border_style="accent", box=box.SIMPLE_HEAD, padding=(0, 2))
    table.add_column("Action", style="bold")
    table.add_column("File")
    
    for action in plan.get("actions", []):
        act_type = action.get("action", "unknown").lower()
        path = action.get("path", "unknown")
        
        style = f"action.{act_type}" if act_type in ["create", "write", "replace", "append"] else "ai"
        if act_type == "delete":
            style = "error" # Red for delete
        elif act_type in ("move", "rename"):
            style = "warning" # Yellow for move
        table.add_row(f"[{style}]{act_type.upper()}[/{style}]", path)
        
    # Indent the table
    console.print(Padding(table, (0, 0, 0, 2)))
    
    # NEW: Show code previews
    for action in plan.get("actions", []):
        act_type = action.get("action", "unknown").lower()
        path = action.get("path", "unknown")
        content = action.get("content", "")
        
        if content and act_type in ["create", "write", "replace", "append"]:
            console.print(f"\n  [accent]📄 {path}[/accent]")
            # Try to guess lexer from suffix
            ext = path.split('.')[-1] if '.' in path else 'txt'
            syntax = Syntax(content, ext, theme="monokai", line_numbers=True, word_wrap=True)
            console.print(Padding(syntax, (0, 0, 1, 4)))
    
    console.print()

def confirm_plan(message: str = None) -> bool:
    """Ask for user confirmation."""
    if message is None:
         message = translate('confirm_apply')
    console.print()
    return Confirm.ask(f"  [warning]{message}[/warning]")

def print_message(sender: str, content: str, style: str = "white"):
    """
    Print a chat message in a clean conversation style.
    """
    # Spacing before message
    console.print()
    
    if sender.lower() in ("you", "user"):
        # We generally don't print user messages anymore (prompt handles it),
        # but if we do (e.g. history), keep it minimal.
        sender_style = "user"
        console.print(f"[{sender_style}]User[/{sender_style}]")
        console.print(Padding(f"[{sender_style}]{content}[/{sender_style}]", (0, 0, 0, 2)))
        
    elif sender.lower() == "gemini":
        sender_style = "ai"
        # Claude-like: Label is just "Gemini" with the theme color
        console.print(f"[{sender_style}]Gemini[/{sender_style}]")
        
        # AI content: Standard markdown rendering, slight indent
        md = Markdown(content)
        console.print(Padding(md, (0, 0, 0, 2)))
        
    else:
        # System/Agent messages
        sender_style = "accent"
        console.print(f"[{sender_style}]{sender}[/{sender_style}]")
        console.print(Padding(f"[info]{content}[/info]", (0, 0, 0, 2)))

    # Add trailing spacing for breathing room before next prompt
    console.print()

def create_spinner(message: str = None):
    """Create a status spinner."""
    if message is None:
        message = translate("thinking")
    return console.status(f"[accent]{message}[/accent]", spinner="dots")
