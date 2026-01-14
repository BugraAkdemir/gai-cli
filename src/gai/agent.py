"""
Agent logic for gai-cli.
Handles intent detection, plan generation, and prompt engineering.
"""

import json
from typing import Dict, Any, Optional

from gai import gemini, scanner, config, ui

SYSTEM_PROMPT = """
You are an expert Autonomous Code Agent.
Your goal is to modify the user's project to fulfill their request.
You will be provided with the Project Context (file structure and contents).

# INSTRUCTIONS
1. Analyze the user request.
2. Decide which files need to be created, modified, or deleted.
3. Output a CHANGE PLAN in strict JSON format.

# JSON OUTPUT FORMAT
You must respond with ONLY this JSON structure. No markdown, no text before/after.
If you cannot return valid JSON, you fail.

{
  "plan": "A short, one-sentence description of what you are doing (in English).",
  "actions": [
    {
      "action": "create",
      "path": "path/to/new/file.ext",
      "content": "FULL FILE CONTENT HERE"
    },
    {
      "action": "write", 
      "path": "path/to/existing/file.ext",
      "content": "FULL NEW CONTENT (OVERWRITES)"
    },
    {
       "action": "append",
       "path": "path/to/logfile.log",
       "content": "CONTENT TO APPEND"
    }
  ]
}

# CRITICAL RULES
- OUTPUT RAW JSON ONLY. Do not wrap in markdown blocks like ```json ... ```.
- **NO REAL NEWLINES INSIDE STRINGS**: Any newline characters in "content" or "plan" MUST be escaped as `\\n`.
- The "plan" field MUST be a single line of text.
- Do not add conversational text like "Here is the plan".
- If the user asks in a different language (e.g. Turkish), UNDERSTAND the intent, but KEEP THE JSON KEYS AND STRUCTURE EXACTLY AS ABOVE.
- "action" must be one of: "create", "write", "replace", "append".
- "content" must be the full file content for create/write.
- "path" must be relative to the project root.
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

def generate_plan(user_request: str) -> Optional[Dict[str, Any]]:
    """
    Generate a modification plan based on user request.
    Retries up to 2 times if JSON is malformed.
    """
    # 1. Scan Project
    ui.print_system("Scanning project files...")
    context = scanner.scan_project()
    ui.print_system(f"Context constructed: {len(context)} chars")
    
    # 2. Construct Prompt
    base_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{context}\n\n"
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
            
        # 4. Parse JSON
        try:
            # Strip markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                # Remove first line (```json or ```)
                lines = lines[1:]
                # Remove last line if it is ``` 
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                clean_text = "\n".join(lines)
            
            # Remove "json" prefix if literal (rare but possible outside markdown)
            if clean_text.lower().startswith("json"):
                 clean_text = clean_text[4:].strip()

            try:
                plan = json.loads(clean_text)
            except json.JSONDecodeError:
                # Fallback: Try ast.literal_eval for python-dict-like strings
                import ast
                plan = ast.literal_eval(clean_text)
            
            # 5. Validate Schema
            if not validate_plan(plan):
                raise ValueError("Parsed JSON does not match expected schema (missing keys or wrong types).")
                
            return plan

        except (json.JSONDecodeError, ValueError, SyntaxError) as e:
            ui.print_error(f"Agent - Invalid Response: {e}")
            
            if attempt < max_retries:
                ui.print_system("Retrying with strict JSON instructions...")
                # Append error instruction to prompt for next attempt
                current_prompt = (
                    f"{base_prompt}\n\n"
                    f"PREVIOUS RESPONSE WAS INVALID JSON. ERROR: {str(e)}\n"
                    f"CRITICAL: YOU MUST RETURN VALID STRICT JSON. NO MARKDOWN. NO COMMENTS.\n"
                    f"ESCAPE NEWLINES IN STRINGS."
                )
            else:
                ui.print_error("Max retries reached. Agent failed to generate a valid plan.")
                ui.print_system(f"Raw Response: {response_text[:500]}...") 
                return None
    return None
