import subprocess
from typing import Dict, Any

from config.tool_config import TECH_STACK_TOOLS

def run_scan(code_path: str, tech: str) -> Dict[str, Any]:
    """
    Runs a suite of validation tools on a given codebase.
    
    Args:
        code_path: The absolute path to the codebase to analyze.
        tech: The technology stack key (e.g., 'python', 'react').
        
    Returns:
        A dictionary containing the results of each tool execution.
    """
    tools = TECH_STACK_TOOLS.get(tech)
    if not tools:
        raise ValueError(f"No tools defined for technology: {tech}")
    
    results = {}
    
    for tool_name, command in tools.items():
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=code_path,
                capture_output=True,
                text=True,
                timeout=120  # Increased timeout
            )
            
            output = result.stdout + result.stderr
            results[tool_name] = {
                "command": command,
                "exit_code": result.returncode,
                "output": output.strip()
            }
            
        except subprocess.TimeoutExpired:
            results[tool_name] = {
                "command": command,
                "error": "Command timed out after 120 seconds."
            }
        except Exception as e:
            results[tool_name] = {
                "command": command,
                "error": f"An unexpected error occurred: {e}"
            }
            
    return results
