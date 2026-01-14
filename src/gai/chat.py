from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from gai import gemini, context, ui, config, agent, fs
from gai.completer import FileContextCompleter

AGENT_KEYWORDS = {
    "add", "create", "make", "write", "update", "modify", "change", "fix", 
    "refactor", "remove", "delete", "move", "rename", 
    "ekle", "oluştur", "yaz", "güncelle", "değiştir", "düzelt", "sil", "taşı"
}

def is_agent_task(text: str) -> bool:
    """Check if the text looks like an agent task."""
    words = set(text.lower().split())
    # Check for intersection with keywords
    if words & AGENT_KEYWORDS:
        return True
    return False

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

    # prompt_toolkit style
    style = Style.from_dict({
        'prompt': 'ansigreen bold',
    })
    
    # Initialize prompt_toolkit session with our completer
    pt_session = PromptSession(
        completer=FileContextCompleter(),
        style=style,
        complete_while_typing=True
    )
    
    ui.console.clear()
    ui.print_header()
    ui.print_system(ui._t("help_hint"))
    
    while True:
        try:
            # Read input using prompt_toolkit for history and autocomplete
            user_input = pt_session.prompt("> ")
            
            cleaned_input = user_input.strip()
            
            if not cleaned_input:
                continue
                
            # Handle Slash Commands
            if cleaned_input.startswith("/"):
                should_continue = handle_command(cleaned_input)
                if not should_continue:
                    break
                continue
                
            if cleaned_input.lower() in ("exit", "quit"):
                ui.print_system(ui._t("goodbye"))
                break
            
            # User input is managed by prompt_toolkit (no double printing)

            # Check Intent: Agent vs Chat
            if is_agent_task(cleaned_input):
                 ui.print_system(ui._t("agent_active"))
                 
                 # Generate Plan
                 with ui.create_spinner(ui._t("agent_planning")):
                     plan = agent.generate_plan(cleaned_input)
                 
                 if plan:
                     # Show Plan
                     ui.print_plan(plan)
                     
                     if plan.get("actions"):
                         # Ask Confirmation
                         if ui.confirm_plan():
                             # Execute
                             ui.print_system(ui._t("applying_changes"))
                             results = fs.apply_actions(plan["actions"])
                             
                             for res in results:
                                 if res["status"] == "success":
                                     ui.print_success(f"✔ {res['message']}")
                                 else:
                                     ui.print_error(f"✖ {res['message']}")
                         else:
                             ui.print_system(ui._t("cancelled"))
                     else:
                         ui.print_system(ui._t("no_actions"))
                 else:
                     ui.print_error(ui._t("plan_failed"))
                     
            else:
                # Normal Chat Flow
                # Process context inclusions
                try:
                    final_prompt = context.process_prompt(cleaned_input)
                except Exception as e:
                    ui.print_error(f"{ui._t('context_error')} {e}")
                    continue
                    
                # Send to Gemini
                with ui.create_spinner():
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
