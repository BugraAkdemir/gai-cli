import typer
from rich.markdown import Markdown

from gai import gemini, context, chat, config, ui

app = typer.Typer(
    name="gai",
    help="Google AI Studio CLI tool.",
    add_completion=False,
)

def onboarding_flow() -> bool:
    """
    Run the first-time setup for API key.
    
    Returns:
        bool: True if setup was successful, False otherwise.
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
        # Check API Key
        if not config.get_api_key():
            if not onboarding_flow():
                raise typer.Exit(code=1)
        
        # Validate Key (optional, but good UX)
        # We'll rely on the actual call to fail if invalid to avoid double latency,
        # or we've implemented validate_api_key in gemini.py if we want to be strict.
        
        if prompt:
            # Agent Mode (One-shot)
            from gai import agent
            try:
                # Process context inline if present
                final_prompt = context.process_prompt(prompt)

                # Generate Plan
                with ui.create_spinner(ui.translate("agent_planning")):
                     plan = agent.generate_plan(final_prompt)
                
                if not plan:
                    ui.print_error(ui.translate("plan_failed"))
                    raise typer.Exit(code=1)

                # Show Plan
                ui.print_plan(plan)
                
                if plan.get("actions"):
                    # One-shot mode currently only SHOWS the plan, doesn't apply?
                    # Or should it apply automatically in one-shot? 
                    # Usually CLI tools apply if prompt is given.
                    # But for safety, let's ask or use a flag. 
                    # User said "whatever I want, it should do it as an agent".
                    # Let's ask for confirmation to be safe.
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
            # Interactive Chat Mode (Default)
            chat.start_chat_session()

def start():
    """Entry point for the script."""
    app()

if __name__ == "__main__":
    start()
