import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed, install them if not."""
    required_packages = [
        "typer[all]",
        "rich",
        "google-genai",
        "prompt_toolkit"
    ]
    
    missing = []
    # Simple check by trying to import main modules
    # Mapping package names to import names
    package_to_import = {
        "typer[all]": "typer",
        "rich": "rich",
        "google-genai": "google.genai",
        "prompt_toolkit": "prompt_toolkit"
    }

    for pkg, imp in package_to_import.items():
        try:
            __import__(imp)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"Missing dependencies found: {', '.join(missing)}")
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("Successfully installed dependencies. Please restart the application.")
            sys.exit(0)
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            print("Please install them manually using: pip install " + " ".join(missing))
            sys.exit(1)

def start():
    """Entry point for the script."""
    # Check dependencies before importing anything heavy
    check_dependencies()
    
    # Delayed imports to handle missing packages
    import typer
    from gai.cli import app
    app()

# Move the Typer app and commands to a place where they won't trigger imports prematurely
# Actually, the 'from gai.cli import app' above handles it if we keep the rest of the file as is
# but we need to make sure the top-level imports in cli.py are safe.

# --- Original Imports (Moved to top of file but inside a check or after check) ---
# We'll keep them at top but we need to ensure check_dependencies runs FIRST.
# The 'gai.cli' import in start() will actually re-import this file.
# To avoid infinite loop and ensure check runs first:
if __name__ == "__main__":
    start()

# --- Everything below this line is the actual CLI logic ---
# It will be imported by 'from gai.cli import app'
try:
    import typer
    from rich.markdown import Markdown
    from gai import gemini, context, chat, config, ui
except ImportError:
    # This might happen during the 'from gai.cli import app' call if check_dependencies 
    # hasn't finished or if it's being imported by another module.
    # But since start() calls check_dependencies() first, we should be fine.
    pass

if 'typer' in sys.modules:
    app = typer.Typer(
        name="gai",
        help="Google AI Studio CLI tool.",
        add_completion=False,
    )

    def onboarding_flow() -> bool:
        """
        Run the first-time setup for API key.
        """
        ui.print_welcome()
        ui.console.print(f"{ui.translate('get_key_link')}\n", style=f"link {ui.translate('get_key_link').split()[-1]}")
        key = ui.console.input(f"[bold yellow]{ui.translate('api_key_prompt')}[/bold yellow] ", password=True)
        if not key.strip():
            ui.print_error(ui.translate("api_key_missing"))
            return False
        config.save_api_key(key.strip())
        ui.print_success(ui.translate("api_key_saved"))
        return True

    @app.callback(invoke_without_command=True)
    def main(
        ctx: typer.Context,
        prompt: str = typer.Argument(None, help="The prompt to send to Gemini. Leave empty for interactive chat."),
    ):
        """
        gai: The Google AI Studio CLI.
        """
        if ctx.invoked_subcommand is None:
            if not config.get_api_key():
                if not onboarding_flow():
                    raise typer.Exit(code=1)
            
            if prompt:
                from gai import agent
                try:
                    final_prompt = context.process_prompt(prompt)
                    with ui.create_spinner(ui.translate("agent_planning")):
                         plan = agent.generate_plan(final_prompt)
                    
                    if not plan:
                        ui.print_error(ui.translate("plan_failed"))
                        raise typer.Exit(code=1)

                    ui.print_plan(plan)
                    
                    if plan.get("actions"):
                        if ui.confirm_plan():
                            ui.print_system(ui.translate("applying_changes"))
                            from gai import fs
                            fs.apply_actions(plan["actions"])
                            ui.print_success("Changes applied.")
                    else:
                        ui.print_system("No modifications suggested.")
                    
                except gemini.InvalidAPIKeyError:
                    ui.print_error("Invalid API Key. Use /apikey in interactive mode or edit ~/.gai/config.json")
                    raise typer.Exit(code=1)
                except gemini.GeminiError as e:
                    ui.print_error(str(e))
                    raise typer.Exit(code=1)
            else:
                chat.start_chat_session()
