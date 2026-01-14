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
    
    ui.console.print("Get your API key here: https://ai.google.dev/\n", style="link https://ai.google.dev/")
    
    key = ui.console.input("[bold yellow]Paste your API key here (hidden):[/bold yellow] ", password=True)
    
    if not key.strip():
        ui.print_error("API key cannot be empty.")
        return False
        
    config.save_api_key(key.strip())
    ui.print_success("API key saved successfully!")
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
            # One-shot mode
            try:
                # Process context inline if present
                final_prompt = context.process_prompt(prompt)

                # Call Gemini API
                # We use ui.create_spinner now
                with ui.create_spinner():
                     response = gemini.generate_response(final_prompt)
                
                # Render Markdown response with UI style
                ui.console.print(Markdown(response))
                
            except gemini.InvalidAPIKeyError:
                ui.print_error("Invalid API Key. Please update it using `gai setup` (todo) or edit ~/.gai/config.json")
                # For now just re-prompt could be nice, but simple error is enough
                # Let's trigger onboarding again?
                ui.console.print("[info]Let's try setting up your key again.[/info]")
                onboarding_flow()
                
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
