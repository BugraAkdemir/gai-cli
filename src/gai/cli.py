import typer
from rich.console import Console

app = typer.Typer(
    name="gai",
    help="Google AI Studio CLI tool.",
    add_completion=False,
)
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    gai: The Google AI Studio CLI.
    """
    if ctx.invoked_subcommand is None:
        console.print("[bold blue]gai-cli[/bold blue] initialized successfully!")
        console.print("Use [bold green]gai --help[/bold green] to see available commands.")

def start():
    """Entry point for the script."""
    app()

if __name__ == "__main__":
    start()
