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

import os
from rich.columns import Columns
from rich.align import Align
from rich.text import Text

def print_header(mode: str = "Agent"):
    """Print the application header in a high-fidelity Claude-style dashboard."""
    import os
    from pathlib import Path
    
    # Get user and system info
    try:
        user_name = os.getlogin()
    except:
        user_name = "User"
    
    cwd = str(Path.cwd())
    version = "v1.6.0" 
    model = config.get_model()
    
    mode_display = f"[success]● {mode} Mode[/success]" if mode == "Agent" else "[warning]○ Chat Mode[/warning]"
    
    # LEFT COLUMN: User Welcome & Logo
    left_content = []
    left_content.append(f"\n[bold]Welcome back {user_name}![/bold]\n")
    # Minimal ASCII-ish Icon
    left_content.append("[accent]      ▐▛███▜▌      [/accent]")
    left_content.append("[accent]     ▝▜█████▛▘     [/accent]")
    left_content.append("[accent]       ▘▘ ▝▝       [/accent]\n")
    left_content.append(f"      {mode_display}\n")
    left_content.append(f"[info]{model} · API Usage Billing[/info]")
    left_content.append(f"[info]{user_name}'s GAI Instance[/info]")
    left_content.append(f"[accent]{cwd}[/accent]")
    
    left_panel = "\n".join(left_content)
    
    # RIGHT COLUMN: Tips & Activity
    right_content = []
    right_content.append("[bold info]Tips for getting started[/bold info]")
    right_content.append("[info]Type /model to switch between Gemini models.[/info]")
    right_content.append("[info]Use @path/to/file to add context to any request.[/info]")
    right_content.append("\n[info]───────────────────────────────────────────────[/info]")
    right_content.append("[bold info]Recent activity[/bold info]")
    right_content.append("[info]No recent activity detected.[/info]")
    
    right_panel = "\n".join(right_content)
    
    # SPLIT TABLE (No borders inside)
    table = Table.grid(expand=True)
    table.add_column(justify="center", ratio=1)
    table.add_column(justify="left", ratio=1)
    table.add_row(left_panel, Padding(right_panel, (1, 0, 0, 4)))
    
    # MAIN OUTER PANEL
    console.print(Panel(
        table,
        title=f"[header] gai-ag {version} [/header]",
        title_align="left",
        border_style="border",
        padding=(0, 2),
        expand=True
    ))
    console.print()

def print_welcome():
    """Print a welcome message for first-time users."""
    print_header()
    # console.print(f"  [info]{translate('welcome')}[/info]", justify="center")
    # console.print(f"  [accent]{translate('api_key_check')}[/accent]\n", justify="center")

def print_error(message: str):
    """Print a styled error message with the Claude-style icon."""
    console.print(f"  [error]⎿  {message}[/error]")

def print_success(message: str):
    """Print a styled success message with the Claude-style icon."""
    console.print(f"  [success]⎿  {message}[/success]")

def print_system(message: str):
    """Print a muted system message with the Claude-style icon."""
    console.print(f"  [accent]⎿  {message}[/accent]")

def print_plan(plan: dict):
    """Display the proposed agent plan with a structured boxed layout."""
    console.print()
    
    plan_elements = []
    
    if plan.get("reasoning"):
        plan_elements.append(f"[info]{plan.get('reasoning')}[/info]\n")
        
    plan_elements.append(f"[ai]{translate('plan_title')}[/ai] {plan.get('plan', 'No description')}\n")
    
    # Action table
    table = Table(
        show_header=True, 
        header_style="accent", 
        border_style="border", 
        box=box.ROUNDED, 
        padding=(0, 1),
        expand=True
    )
    table.add_column("Action", style="bold", width=12)
    table.add_column("Path")
    
    for action in plan.get("actions", []):
        act_type = action.get("action", "unknown").lower()
        path = action.get("path", "unknown")
        
        style = f"action.{act_type}" if act_type in ["create", "write", "replace", "append"] else "ai"
        if act_type == "delete":
            style = "error"
        elif act_type in ("move", "rename"):
            style = "warning"
        table.add_row(f"[{style}]{act_type.upper()}[/{style}]", path)
    
    plan_elements.append(table)
    
    # Layout everything in a main plan panel
    console.print(Panel(
        *plan_elements,
        title="[header] Proposed Plan [/header]",
        border_style="accent",
        padding=(1, 2)
    ))

    # CodePreviews in their own panels
    for action in plan.get("actions", []):
        act_type = action.get("action", "unknown").lower()
        path = action.get("path", "unknown")
        content = action.get("content", "")
        
        if content and act_type in ["create", "write", "replace", "append"]:
            ext = path.split('.')[-1] if '.' in path else 'txt'
            syntax = Syntax(content, ext, theme="monokai", line_numbers=True, word_wrap=True)
            console.print(Panel(
                syntax,
                title=f"[accent] {path} [/accent]",
                border_style="border",
                padding=(0, 1)
            ))
    
    console.print()

def confirm_plan(message: str = None) -> bool:
    """Ask for user confirmation in a distinctive style."""
    if message is None:
         message = translate('confirm_apply')
    console.print()
    return Confirm.ask(f"  [warning]⚡ {message}[/warning]")

def print_message(sender: str, content: str, style: str = "white"):
    """
    Print a chat message in a clean conversation style with Claude-like panels.
    """
    if sender.lower() in ("you", "user"):
        # Minimal for user
        console.print()
        console.print(f"  [user]You[/user]")
        console.print(Padding(content, (0, 0, 0, 4)))
        
    elif sender.lower() == "gemini":
        console.print()
        # Boxed AI response
        md = Markdown(content)
        console.print(Panel(
            md,
            title="[ai] Gemini [/ai]",
            title_align="left",
            border_style="ai",
            padding=(1, 2),
            subtitle=f"[dim]Powered by {config.get_model()}[/dim]",
            subtitle_align="right"
        ))
    else:
        # System/Agent messages
        console.print()
        console.print(Panel(
            f"[info]{content}[/info]",
            title=f"[accent] {sender} [/accent]",
            border_style="accent",
            padding=(0, 2)
        ))

    console.print()

def create_spinner(message: str = None):
    """Create a status spinner with a clean look."""
    if message is None:
        message = translate("thinking")
    return console.status(f"  [accent]{message}[/accent]", spinner="dots")

def print_footer():
    """Print the application footer with helpful shortcuts."""
    footer_content = [
        ("! for bash mode", "double tap esc to clear input"),
        ("/ for commands", "shift + tab to auto-accept edits"),
        ("@ for file paths", "ctrl + o for verbose output"),
        ("& for background", "ctrl + t to show todos")
    ]
    
    table = Table.grid(expand=True, padding=(0, 4))
    table.add_column(justify="left")
    table.add_column(justify="left")
    
    for left, right in footer_content:
        table.add_row(f"[info]{left}[/info]", f"[info]{right}[/info]")
    
    console.print(Padding(table, (0, 0, 0, 4)))
    console.print("[dim]────────────────────────────────────────────────────────────────────────────────[/dim]")
