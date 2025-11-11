#!/usr/bin/env python3
"""
Simple Motor - Minimal Notebook Orchestrator

Startet ein einzelnes Notebook mit Parametern.
Nichts kompliziertes. Nur: Input → Notebook → Output.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import argparse


class SimpleMotor:
    """Minimal orchestrator that runs one notebook with parameters"""

    def __init__(self):
        self.notebook_path = Path(__file__).parent / "workflow.ipynb"
        self.output_dir = Path(__file__).parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    def run(self, project: str, request: str, code_path: str, tech_stack: str):
        """Run the workflow notebook with parameters"""

        print("\n" + "="*60)
        print("🔧 SIMPLE MOTOR")
        print("="*60)
        print(f"Project: {project}")
        print(f"Request: {request}")
        print(f"Code: {code_path}")
        print(f"Tech: {tech_stack}")
        print("="*60 + "\n")

        # Check if notebook exists
        if not self.notebook_path.exists():
            print(f"✗ Notebook not found: {self.notebook_path}")
            return False

        # Run with papermill
        output_notebook = self.output_dir / f"{project}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"

        print(f"Running workflow...")
        print(f"Output: {output_notebook}\n")

        try:
            # Execute with papermill
            cmd = [
                "jupyter", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--ExecutePreprocessor.timeout=600",
                f"--output={output_notebook}",
                "--output-dir=/tmp",
                str(self.notebook_path)
            ]

            # Try with papermill if available
            try:
                import papermill as pm
                pm.execute_notebook(
                    str(self.notebook_path),
                    str(output_notebook),
                    parameters={
                        "project_name": project,
                        "client_request": request,
                        "code_path": code_path,
                        "tech_stack": tech_stack,
                        "execution_time": datetime.now().isoformat()
                    }
                )
                print(f"\n✓ Notebook executed successfully")
                print(f"Output: {output_notebook}")
                return True
            except ImportError:
                # Fallback: use nbconvert
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if result.returncode == 0:
                    print(f"\n✓ Notebook executed successfully")
                    print(f"Output: {output_notebook}")
                    return True
                else:
                    print(f"✗ Execution failed: {result.stderr}")
                    return False

        except subprocess.TimeoutExpired:
            print("✗ Execution timeout")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Simple Motor - Run analysis workflow")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--request", required=True, help="What to analyze")
    parser.add_argument("--code-path", default="/tmp", help="Path to code")
    parser.add_argument("--tech-stack", default="python", help="Technology stack")

    args = parser.parse_args()

    motor = SimpleMotor()
    success = motor.run(args.project, args.request, args.code_path, args.tech_stack)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
