import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from gai import gemini, context, ui, config, agent, fs
from gai.completer import FileContextCompleter
from typing import List
from pathlib import Path

# Redundant keywords for intent detection (kept for documentation)
AGENT_KEYWORDS = {
    "add", "create", "make", "write", "update", "modify", "change", "fix", 
    "refactor", "remove", "delete", "move", "rename", 
    "ekle", "oluştur", "yaz", "güncelle", "değiştir", "düzelt", "sil", "taşı"
}

# Mode state
AGENT_MODE = True

def get_test_command() -> List[str]:
    """Detect project type and return the appropriate test command."""
    cwd = Path(".")
    
    # Flutter
    if (cwd / "pubspec.yaml").exists():
        return ["flutter", "test"]
    
    # Node.js
    if (cwd / "package.json").exists():
        return ["npm", "test"]
        
    # Python (Default)
    return [sys.executable, "-m", "pytest", "-v"]

def handle_command(command: str) -> bool:
    """
    Handle chat slash commands.
    
    Returns:
        bool: True if loop should continue, False if it should break (exit).
    """
    cmd_parts = command.lower().split()
    cmd = cmd_parts[0]
    
    if cmd == "/exit":
        ui.print_system("Goodbye.")
        return False
        
    elif cmd == "/clear":
        ui.console.clear()
        ui.print_header()
        ui.print_system(ui.translate("help_hint"))
        return True
        
    elif cmd == "/help":
        ui.print_system(ui.translate("help_title"))
        ui.print_system(ui.translate("help_desc"))
        ui.print_system("  /newchat - Clear history and start a new session")
        return True
        
    elif cmd == "/apikey":
        ui.print_system("Updating API Key configuration...")
        from gai.cli import onboarding_flow
        onboarding_flow()
        return True
    
    elif cmd == "/theme":
        if len(cmd_parts) < 2:
            ui.print_system("Usage: /theme [default|dark|light]")
            return True
        new_theme = cmd_parts[1]
        if new_theme not in ["default", "dark", "light"]:
             ui.print_error(f"Unknown theme: {new_theme}")
             return True
        
        config.save_theme(new_theme)
        ui.reload_ui()
        ui.print_success(f"Theme set to {new_theme}")
        return True

    elif cmd == "/lang":
         if len(cmd_parts) < 2:
            ui.print_system("Usage: /lang [en|tr]")
            return True
         new_lang = cmd_parts[1]
         if new_lang not in ["en", "tr"]:
             ui.print_error(f"Unknown language: {new_lang}")
             return True
             
         config.save_language(new_lang)
         # In a real app we might need to reload more stuff, but here mostly UI text
         ui.print_success(f"Language set to {new_lang}")
         ui.print_system(ui.translate("welcome")) # Verify switch
         return True
    
    
    elif cmd == "/model":
        # Define available models with metadata
        models = [
            {
                "name": "gemini-2.0-flash-exp",
                "display": "Gemini 2.0 Flash (Experimental)",
                "speed": "Fastest",
                "context": "1M tokens",
                "pricing": "Free tier available"
            },
            {
                "name": "gemini-2.0-flash-lite",
                "display": "Gemini 2.0 Flash Lite",
                "speed": "Fastest",
                "context": "1M tokens",
                "pricing": "Free tier available"
            },
            {
                "name": "gemini-1.5-flash",
                "display": "Gemini 1.5 Flash",
                "speed": "Fast",
                "context": "1M tokens",
                "pricing": "$0.075/$0.30 per 1M tokens"
            },
            {
                "name": "gemini-1.5-pro",
                "display": "Gemini 1.5 Pro",
                "speed": "Moderate",
                "context": "2M tokens",
                "pricing": "$1.25/$5.00 per 1M tokens"
            }
        ]
        
        current_model = config.get_model()
        
        # If model name is provided, switch directly
        if len(cmd_parts) >= 2:
            new_model = cmd_parts[1]
            model_names = [m["name"] for m in models]
            
            if new_model not in model_names:
                ui.print_error(f"Unknown model: {new_model}")
                ui.print_system("Available models: " + ", ".join(model_names))
                return True
            
            config.save_model(new_model)
            ui.print_success(f"Model set to {new_model}")
            ui.print_system("New sessions will use this model.")
            return True
        
        # Interactive selection
        # Use Rich Table for better display
        from rich.table import Table
        from rich.panel import Panel
        from rich import box as rich_box
        
        table = Table(
            show_header=True, 
            header_style="accent", 
            border_style="border", 
            box=rich_box.ROUNDED, 
            show_lines=True,
            expand=True
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Model", style="bold")
        table.add_column("Speed", justify="center")
        table.add_column("Context Window", justify="center")
        table.add_column("Pricing (Input/Output)", justify="right")
        
        for idx, model in enumerate(models, 1):
            marker = "›" if model["name"] == current_model else " "
            name_display = f"{marker} {model['display']}"
            if model["name"] == current_model:
                name_display = f"[success]{name_display}[/success]"
            
            table.add_row(
                str(idx),
                name_display,
                model["speed"],
                model["context"],
                model["pricing"]
            )
        
        ui.console.print(Panel(
            table,
            title="[header] Available Gemini Models [/header]",
            subtitle="[dim]Current model marked with ›[/dim]",
            border_style="accent",
            padding=(1, 2)
        ))
        ui.console.print()
        
        # Prompt for selection
        try:
            choice = ui.console.input("[accent]Select a model (1-{}) or press Enter to cancel:[/accent] ".format(len(models)))
            
            if not choice.strip():
                ui.print_system("Cancelled.")
                return True
            
            try:
                choice_num = int(choice.strip())
                if 1 <= choice_num <= len(models):
                    selected_model = models[choice_num - 1]
                    config.save_model(selected_model["name"])
                    ui.print_success(f"Model set to {selected_model['display']}")
                    ui.print_system("New sessions will use this model.")
                else:
                    ui.print_error("Invalid selection. Please choose a number from the list.")
            except ValueError:
                ui.print_error("Please enter a valid number.")
        except KeyboardInterrupt:
            ui.console.print()
            ui.print_system("Cancelled.")
        
        return True
        
        
    elif cmd == "/newchat":
        config.clear_history()
        ui.print_success("History cleared. Starting a new session.")
        return "RESET"
        
    elif cmd == "/info":
        # Look for info.txt in the package directory
        info_path = Path(__file__).parent / "info.txt"
        
        # Fallback to CWD (for dev repo root)
        if not info_path.exists():
            info_path = Path("info.txt")
            
        if info_path.exists():
            try:
                from rich.panel import Panel
                content = info_path.read_text(encoding="utf-8")
                ui.console.print(Panel(content.strip(), title="[accent]Application Info[/accent]", border_style="accent"))
            except Exception as e:
                ui.print_error(f"Could not read info.txt: {e}")
        else:
            ui.print_error("info.txt not found. Please ensure it exists in the package directory.")
        return True
        
    elif cmd == "/chat":
        global AGENT_MODE
        AGENT_MODE = not AGENT_MODE
        status = "ENABLED" if AGENT_MODE else "DISABLED"
        ui.print_success(f"Agent mode is now {status}.")
        if not AGENT_MODE:
            ui.print_system("Conversation mode active. I will focus on chatting.")
        else:
            ui.print_system("Agent mode active. I can help with file operations.")
        return True
        
    else:
        ui.print_system(ui.translate("unknown_command"))
        return True


def start_chat_session():
    """
    Start the professional interactive chat session.
    """
    try:
        session = gemini.ChatSession()
    except Exception as e:
        ui.print_error(f"Initializing Gemini: {e}")
        return

    style = Style.from_dict({
        '': '#ffffff',
    })
    
    pt_session = PromptSession(style=style)
    
    current_mode = "Agent" if AGENT_MODE else "Chat"
    ui.print_header(mode=current_mode)
    ui.print_system(ui.translate("help_hint"))
    ui.print_footer()
    
    # Load persistent history
    agent_history = config.load_history()
    if agent_history:
        ui.print_system(f"Resuming previous session ({len(agent_history)} turns). Use /newchat to start fresh.")

    while True:
        try:
            # Read input
            user_input = pt_session.prompt("❯ ")
            cleaned_input = user_input.strip()
            
            if not cleaned_input:
                continue
                
            # Handle Slash Commands
            if cleaned_input.startswith("/"):
                cmd_result = handle_command(cleaned_input)
                if cmd_result == "RESET":
                    agent_history = []
                    continue
                if not cmd_result:
                    break
                continue
                
            if cleaned_input.lower() in ("exit", "quit"):
                ui.print_system(ui.translate("goodbye"))
                break

            # --- CHAT MODE (Simple Conversation) ---
            if not AGENT_MODE:
                with ui.create_spinner(ui.translate("thinking")):
                    response = gemini.generate_response(cleaned_input, history=agent_history)
                
                ui.print_message("Gemini", response)
                agent_history.append({"role": "user", "content": cleaned_input})
                agent_history.append({"role": "model", "content": response})
                config.save_history(agent_history)
                continue

            # --- AGENT MODE (Autonomous Planning & Execution) ---
            ui.print_system(ui.translate("agent_active"))
            current_request = cleaned_input
            
            while True:
                try:
                    with ui.create_spinner(ui.translate("agent_planning")):
                        plan = agent.generate_plan(current_request, history=agent_history)
                except gemini.InvalidAPIKeyError as e:
                    ui.print_error(f"Authentication Error: {str(e)}")
                    ui.print_system("Use /apikey to update your API key if needed.")
                    break
                except gemini.GeminiError as e:
                    ui.print_error(f"API Error: {str(e)}")
                    ui.print_system("There may be a temporary issue with the Gemini API. Please try again.")
                    break
                except Exception as e:
                    ui.print_error(f"Unexpected error during planning: {str(e)}")
                    break
                
                if not plan:
                    ui.print_error(ui.translate("plan_failed"))
                    break

                # Show Plan / Analysis
                ui.print_plan(plan)
                
                # If no actions, just show result and break loop (return to prompt)
                if not plan.get("actions"):
                    # Save to history for context
                    agent_history.append({"role": "user", "content": current_request})
                    agent_history.append({"role": "assistant", "content": plan.get("reasoning", "Analysis complete.")})
                    config.save_history(agent_history)
                    break

                # Ask Confirmation for modifications
                confirm_msg = ui.translate("confirm_apply")
                if ui.confirm_plan(message=confirm_msg):
                    # Execute
                    ui.print_system(ui.translate("applying_changes"))
                    results = fs.apply_actions(plan["actions"])
                    
                    success = True
                    for res in results:
                        if res["status"] == "success":
                            ui.print_success(f"✔ {res['message']}")
                        else:
                            ui.print_error(f"✖ {res['message']}")
                            success = False
                    
                    # Save state/history after success
                    summary = f"Applied plan: {plan.get('plan', 'No summary')}"
                    agent_history.append({"role": "user", "content": current_request})
                    agent_history.append({"role": "assistant", "content": summary})
                    config.save_history(agent_history)
                    
                    # Update project brain
                    config.save_state({
                        "last_task": current_request,
                        "status": "applying",
                        "errors": []
                    }, root=Path("."))

                    # Automaton: Run Tests and Self-Correct
                    if success:
                        ui.print_system("Running verification tests...")
                        import subprocess
                        try:
                            test_cmd = get_test_command()
                            ui.print_system(f"Executing: {' '.join(test_cmd)}")
                            
                            try:
                                test_result = subprocess.run(
                                    test_cmd,
                                    capture_output=True, 
                                    text=True, 
                                    cwd=".",
                                    encoding="utf-8",
                                    errors="replace",
                                    shell=True if sys.platform == "win32" else False,
                                    timeout=120 # 2 minute limit
                                )
                                stdout = test_result.stdout or ""
                                stderr = test_result.stderr or ""
                                returncode = test_result.returncode
                            except subprocess.TimeoutExpired as te:
                                ui.print_error("Tests timed out.")
                                stdout = te.stdout or ""
                                stderr = te.stderr or ""
                                returncode = 1
                            except Exception as e:
                                ui.print_error(f"Execution error: {e}")
                                stdout = ""
                                stderr = str(e)
                                returncode = 1
                            
                            if returncode == 0:
                                ui.print_success("Tests passed! Task completed.")
                                config.save_state({
                                    "last_task": current_request,
                                    "status": "completed",
                                    "errors": []
                                }, root=Path("."))
                                break
                            else:
                                # Check if we modified any source files that would affect tests
                                modified_paths = [action.get("path", "") for action in plan.get("actions", [])]
                                modified_src = any(
                                    p.startswith("src/") or p.startswith("lib/") or p.endswith(".py") or p.endswith(".dart")
                                    for p in modified_paths if not p.startswith("tests/")
                                )
                                
                                # Only attempt self-correction if we modified actual source code
                                if modified_src:
                                    ui.print_error("Tests failed. Attempting self-correction...")
                                    error_log = stdout + "\n" + stderr
                                    config.save_state({
                                        "last_task": current_request,
                                        "status": "failed",
                                        "errors": [line for line in error_log.splitlines() if "error" in line.lower()][:5]
                                    }, root=Path("."))
                                    current_request = f"The previous changes caused test failures:\n\n{error_log}\n\nPlease fix the errors in the files you modified. DO NOT modify test files."
                                    # Continue to next iteration for self-correction
                                else:
                                    # We only modified non-source files (e.g., analysis.txt), so don't retry
                                    ui.print_error("Tests failed, but the changes were unrelated to source code.")
                                    ui.print_system("Test failures appear to be pre-existing. Skipping self-correction.")
                                    config.save_state({
                                        "last_task": current_request,
                                        "status": "completed_with_test_warnings",
                                        "errors": []
                                    }, root=Path("."))
                                    break
                        except Exception as e:
                            ui.print_error(f"Test execution failed: {e}")
                            break
                    else:
                        break
                else:
                    ui.print_system(ui.translate("cancelled"))
                    break
            
        except KeyboardInterrupt:
            ui.print_system("\nGoodbye.")
            break
        except EOFError:
            ui.print_system("\nGoodbye.")
            break
