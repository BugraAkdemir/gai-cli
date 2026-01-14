"""
Agent logic for gai-cli.
Handles intent detection, plan generation, and prompt engineering.
"""

import json
import re
import ast
from typing import Dict, Any, Optional, List

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
  "plan": "Step-by-step description (can be string or list)",
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
- **IMPORTANT**: If your code contains triple quotes, use double triple-quotes or escape them as `\\'\\'\\'`.
- **NO COMMENTS** inside the dictionary.
- "action" must be one of: "create", "write", "replace", "append", "delete", "move".
- Follow existing project patterns and architecture.
- **TESTING**: If you modify code, assume the project has its own test suite (e.g., `flutter test`). DO NOT try to run tests as part of your `actions`. Tests are run automatically AFTER you apply changes. If you want to verify the current state without changes, suggest NO actions and I will ask the user to run tests.
- **VERIFICATION**: If you are provided with error logs and believe your previous fix was correct, you should double-check the logic. If you are SURE it's correct but tests still fail, look for environment issues or misconfigurations in your plan.
- **INFORMATION & ANALYSIS**: If the user asks a question or for an analysis (like "Explain this project"), provide the full answer/analysis in the "reasoning" field and leave the "actions" list EMPTY.
- **SELF-CORRECTION SCOPE**: If tests fail after your changes, ONLY fix errors that are DIRECTLY caused by the files YOU modified. NEVER modify test files (tests/*) during self-correction. If tests fail due to pre-existing issues unrelated to your changes, simply report the failure and stop.
"""

def validate_plan(plan_data: Any) -> bool:
    """Validate the agent plan structure."""
    if not isinstance(plan_data, dict):
        return False
    
    required_keys = ["reasoning", "plan", "actions"]
    if not all(k in plan_data for k in required_keys):
        return False
    
    if not isinstance(plan_data["reasoning"], str):
        return False
    if not isinstance(plan_data["plan"], (str, list)): 
        return False
    if not isinstance(plan_data["actions"], list):
        return False
        
    for action in plan_data.get("actions", []):
        if not isinstance(action, dict):
            return False
        if not all(k in action for k in ["action", "path"]):
            return False
            
    return True

def clean_llm_response(text: str) -> str:
    """Clean LLM response for robust parsing."""
    # Remove markdown blocks if present
    text = re.sub(r'```(?:python|json)?\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    return text.strip()

def parse_plan(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse a plan from raw LLM text using multiple strategies.
    Handles unescaped backslashes and other common LLM output issues.
    """
    content = clean_llm_response(text)
    
    # Strategy 1: Find the dict and try literal_eval
    dict_match = re.search(r'\{.*\}', content, re.DOTALL)
    if not dict_match:
        return None
        
    dict_str = dict_match.group(0)

    # Attempt 1: Standard ast.literal_eval
    try:
        plan_data = ast.literal_eval(dict_str)
        if validate_plan(plan_data):
            return plan_data
    except Exception:
        pass

    # Attempt 2: Handle common backslash issues (e.g. C:\Users)
    try:
        # Escape backslashes that are not part of a valid escape sequence
        # We look for a backslash that is NOT followed by another backslash or n, r, t, ", ', u, x
        fixed_str = re.sub(r'\\(?![\\nrt"\'ux])', r'\\\\', dict_str)
        plan_data = ast.literal_eval(fixed_str)
        if validate_plan(plan_data):
            return plan_data
    except Exception:
        pass

    # Attempt 3: JSON fallback
    try:
        # JSON is stricter about quotes and escapes
        # We try to clean it for JSON
        json_clean = dict_str.replace("'''", '"').replace("'", '"')
        plan_data = json.loads(json_clean)
        if validate_plan(plan_data):
            return plan_data
    except Exception:
        pass

    return None

def generate_plan(user_request: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[Dict[str, Any]]:
    """
    Generate a modification plan based on user request.
    Handles scanning, prompting, and retry logic.
    """
    # 1. Scanning
    with ui.create_spinner(ui.translate("agent_scanning")):
        project_context = scanner.scan_project()
    
    # 2. Build Prompt
    prompt = (
        f"## PROJECT CONTEXT\n{project_context}\n"
        f"## USER REQUEST\n{user_request}"
    )
    
    current_prompt = prompt
    max_retries = 2
    
    for attempt in range(max_retries + 1):
        if attempt > 0:
            ui.print_system(f"Retrying with stricter format instructions (Attempt {attempt+1})...")
            
        try:
            response_text = gemini.generate_response(
                current_prompt, 
                history=history,
                system_instruction=SYSTEM_PROMPT
            )
            
            # 4. Parse Response
            plan = parse_plan(response_text)
            if plan:
                return plan
            
            # If parsing fails, refine prompt for retry
            ui.print_error(f"Agent - Parsing Failed (Attempt {attempt+1})")
            current_prompt = (
                f"{prompt}\n\n"
                f"ERROR: Your last response could not be parsed as a Python dictionary.\n"
                f"STRICT INSTRUCTION: Return ONLY the dictionary starting with '{{' and ending with '}}'.\n"
                f"Use triple single-quotes (''' ) for 'content' fields. DO NOT use markdown code blocks."
            )
        except gemini.InvalidAPIKeyError:
            raise
        except Exception as e:
            ui.print_error(f"Agent - Gemini Error: {e}")
            break

    ui.print_error("Failed to generate a valid plan after retries.")
    return None
