import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from gai import gemini, context, ui, config, agent, fs
from gai.completer import FileContextCompleter
from typing import List
from pathlib import Path

AGENT_KEYWORDS = {
    "add", "create", "make", "write", "update", "modify", "change", "fix", 
    "refactor", "remove", "delete", "move", "rename", 
    "ekle", "oluştur", "yaz", "güncelle", "değiştir", "düzelt", "sil", "taşı"
}

def is_agent_task(text: str) -> bool:
    """Check if the text looks like an agent task."""
    text_lower = text.lower()
    words = text_lower.split()
    
    # Check if ANY keyword is present as a full word
    for kw in AGENT_KEYWORDS:
        if kw in words:
            return True
            
    # Substring matches for Turkish suffixes (e.g. 'ekle', 'eklesene')
    turkish_triggers = ["yap", "oluştur", "ekle", "sil", "taşı", "düzelt"]
    for trigger in turkish_triggers:
        if trigger in text_lower and len(text_lower) < 50: # Limit length for safety
             return True

    return False

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
        ui.print_system(ui._t("help_hint"))
        return True
        
    elif cmd == "/help":
        ui.print_system(ui._t("help_title"))
        ui.print_system(ui._t("help_desc"))
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
         ui.print_system(ui._t("welcome")) # Verify switch
         return True
    
    elif cmd == "/model":
        current = config.get_model()
        ui.print_system(f"Current Model: {current}")
        return True
        
    elif cmd == "/newchat":
        config.clear_history()
        ui.print_success("History cleared. Starting a new session.")
        return "RESET"
        
    else:
        ui.print_system(ui._t("unknown_command"))
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
    
    ui.print_header()
    ui.print_system(ui._t("help_hint"))
    
    # Load persistent history
    agent_history = config.load_history()
    if agent_history:
        ui.print_system(f"Resuming previous session ({len(agent_history)} turns). Use /newchat to start fresh.")

    while True:
        try:
            # Read input
            user_input = pt_session.prompt("> ")
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
                ui.print_system(ui._t("goodbye"))
                break

            # Check Intent: Agent vs Chat
            if is_agent_task(cleaned_input):
                 ui.print_system(ui._t("agent_active"))
                 current_request = cleaned_input
                 
                 while True:
                     # Generate Plan
                     with ui.create_spinner(ui._t("agent_planning")):
                         plan = agent.generate_plan(current_request, history=agent_history)
                     
                     if not plan:
                         ui.print_error(ui._t("plan_failed"))
                         break

                     # Show Plan
                     ui.print_plan(plan)
                     
                     if not plan.get("actions"):
                         ui.print_system(ui._t("no_actions"))
                         break

                     # Ask Confirmation
                     if ui.confirm_plan():
                         # Execute
                         ui.print_system(ui._t("applying_changes"))
                         results = fs.apply_actions(plan["actions"])
                         
                         success = True
                         for res in results:
                             if res["status"] == "success":
                                 ui.print_success(f"✔ {res['message']}")
                             else:
                                 ui.print_error(f"✖ {res['message']}")
                                 success = False
                         
                         # Save state/history after success (only the user request and a summary)
                         summary = f"Applied plan: {plan.get('plan', 'No summary')}"
                         agent_history.append({"role": "user", "content": current_request})
                         agent_history.append({"role": "assistant", "content": summary})
                         config.save_history(agent_history)
                         
                         # Update project brain
                         config.save_state({
                             "last_task": current_request,
                             "status": "applying",
                             "errors": []
                         })

                         # Automaton: Run Tests and Self-Correct
                         if success:
                             ui.print_system("Running verification tests...")
                             import subprocess
                             try:
                                 test_cmd = get_test_command()
                                 ui.print_system(f"Executing: {' '.join(test_cmd)}")
                                 
                                 test_result = subprocess.run(
                                     test_cmd,
                                     capture_output=True, 
                                     text=True, 
                                     cwd=".",
                                     encoding="utf-8",
                                     errors="replace",
                                     shell=True if sys.platform == "win32" else False
                                 )
                                 
                                 stdout = test_result.stdout or ""
                                 stderr = test_result.stderr or ""
                                 
                                 if test_result.returncode == 0:
                                     ui.print_success("Tests passed! Task completed.")
                                     config.save_state({
                                         "last_task": current_request,
                                         "status": "completed",
                                         "errors": []
                                     }, root=Path("."))
                                     break
                                 else:
                                     ui.print_error("Tests failed. Attempting self-correction...")
                                     error_log = stdout + "\n" + stderr
                                     config.save_state({
                                         "last_task": current_request,
                                         "status": "failed",
                                         "errors": [line for line in error_log.splitlines() if "error" in line.lower()][:5]
                                     }, root=Path("."))
                                     current_request = f"The previous changes caused test failures:\n\n{error_log}\n\nPlease fix the errors."
                                     continue
                             except Exception as e:
                                 ui.print_system(f"Auto-test skipped or failed: {e}")
                                 break
                         else:
                             break
                     else:
                         ui.print_system(ui._t("cancelled"))
                         break
            else:
                # Normal Chat Flow
                # Process context inclusions
                try:
                    final_prompt = context.process_prompt(cleaned_input)
                except Exception as e:
                    ui.print_error(f"{ui._t('context_error')} {e}")
                    continue
                    
                # Send to Gemini
                with ui.create_spinner(ui._t("thinking")):
                    try:
                        response = session.send_message(final_prompt)
                    except gemini.InvalidAPIKeyError:
                        ui.print_error("Invalid API Key. Please use /apikey to reset it.")
                        continue
                    except gemini.GeminiError as e:
                        ui.print_error(f"{ui._t('gemini_error')} {str(e)}")
                        continue

                # Render AI Response
                ui.print_message("Gemini", response)
            
        except KeyboardInterrupt:
            ui.print_system("\nGoodbye.")
            break
        except EOFError:
            ui.print_system("\nGoodbye.")
            break
