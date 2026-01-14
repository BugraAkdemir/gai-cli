"""
Agent logic for gai-cli.
Handles intent detection, plan generation, and prompt engineering.
"""

import json
from typing import Dict, Any, Optional

from gai import gemini, scanner, config, ui

SYSTEM_PROMPT = """
You are an expert Autonomous Code Agent (similar to Cursor or Devin).
Your goal is to modify the user's project to fulfill their request EXACTLY and COMPLETELY.

# CRITICAL PHILOSOPHY
- **COMPLETE THE JOB**: Do not leave things half-finished. If a task requires multiple steps, plan them all or execute the first major step and indicate what's next.
- **READ BEFORE WRITE**: Analyze existing code carefully.
- **NO PLACEHOLDERS**: Generate full, working code. Never use "code goes here" or comments like "implement logic here".
- **SELF-CORRECTION**: If you are provided with error logs, ANALYZE them and fix your previous code.

# PROJECT CONTEXT
You will be provided with the Project Context (file structure and contents).

# OUTPUT FORMAT: PYTHON DICTIONARY
You must respond with a VALID PYTHON DICTIONARY.
REQUIRED STRUCTURE:
{
  "reasoning": "...",
  "plan": "...",
  "actions": [
    {
      "action": "...",
      "path": "...",
      "content": '''...'''
    }
  ]
}

# CRITICAL RULES
- Output ONLY the raw dictionary. DO NOT wrap it in markdown code blocks like ```python.
- Use Python triple quotes (''' ) for the "content" field to handle multi-line code safely.
- **NO COMMENTS** inside the dictionary.
- If the code you are writing contains triple quotes, escape them or use double triple-quotes.
- "action" must be one of: "create", "write", "replace", "append", "delete", "move".
- Follow existing project patterns and architecture.
"""

def validate_plan(plan: Any) -> bool:
    """Validate that the plan follows the expected schema."""
    if not isinstance(plan, dict):
        return False
    if "plan" not in plan or not isinstance(plan["plan"], str):
        return False
    if "actions" not in plan or not isinstance(plan["actions"], list):
        return False
    for action in plan["actions"]:
        if not isinstance(action, dict):
            return False
        if "action" not in action or "path" not in action:
            return False
        # content is optional for some actions? prompt says create/write needs it.
        # But for schema validation, just checking existence is good enough for now.
    return True

def generate_plan(user_request: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[Dict[str, Any]]:
    """
    Generate a modification plan based on user request.
    history: List of previous turns for context.
    """
    # 1. Scan Project
    ui.print_system("Scanning project files...")
    project_context = scanner.scan_project()
    ui.print_system(f"Context constructed: {len(project_context)} chars")
    
    # 2. Construct Prompt
    # Format history if exists
    history_str = ""
    if history:
        history_str = "\n## SESSION HISTORY\n"
        for turn in history:
            role = "AGENT" if turn['role'] == 'assistant' else "USER"
            history_str += f"{role}: {turn['content']}\n"

    base_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{project_context}\n\n"
        f"{history_str}\n"
        f"USER REQUEST: {user_request}"
    )
    
    current_prompt = base_prompt
    max_retries = 2
    
    for attempt in range(max_retries + 1):
        # 3. Call Gemini
        ui.print_system(f"Waiting for Gemini (Attempt {attempt+1}/{max_retries+1})...")
        try:
            response_text = gemini.generate_response(current_prompt)
        except Exception as e:
            ui.print_error(f"Agent - Gemini Call Failed: {e}")
            return None
            
        # 4. Parse Response
        try:
            clean_text = response_text.strip()
            
            # Robust extraction: find the first '{' and last '}'
            import re
            match = re.search(r'(\{.*\})', clean_text, re.DOTALL)
            if match:
                clean_text = match.group(1)
            
            # Remove markdown delimiters if they survived regex
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].strip() == "```": lines = lines[:-1]
                clean_text = "\n".join(lines)

            # Attempt parsing
            import ast
            try:
                # ast.literal_eval is safer and handles Python triple quotes perfectly
                plan = ast.literal_eval(clean_text)
            except (SyntaxError, ValueError):
                # Fallback to JSON if it looks more like JSON
                import json
                plan = json.loads(clean_text)
            
            # 5. Validate Schema
            if not validate_plan(plan):
                raise ValueError("Parsed plan does not match expected schema.")
                
            return plan

        except Exception as e:
            ui.print_error(f"Agent - Parsing Failed (Attempt {attempt+1}): {e}")
            
            if attempt < max_retries:
                ui.print_system("Retrying with stricter format instructions...")
                current_prompt = (
                    f"{base_prompt}\n\n"
                    f"ERROR IN PREVIOUS RESPONSE: {str(e)}\n"
                    f"STRICT INSTRUCTION: Return ONLY a valid Python dictionary starting with '{{' and ending with '}}'.\n"
                    f"Use triple single-quotes (''' ) for code blocks."
                )
            else:
                ui.print_error("Max retries reached. Raw response follows:")
                ui.console.print(response_text)
                return None
    return None
