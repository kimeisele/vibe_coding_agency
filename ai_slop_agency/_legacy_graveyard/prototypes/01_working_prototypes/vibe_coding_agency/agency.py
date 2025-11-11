#!/usr/bin/env python3
"""
Vibe Coding Agency - CLI Orchestrator
Loads and executes the Grand Agency Code Framework
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from enum import Enum


class ProjectType(Enum):
    NEW = "new_project"
    EXISTING = "existing_project"


class Phase(Enum):
    INTAKE = 1
    ARCHITECTURE = 2
    IMPLEMENTATION = 3
    CODE_GENERATION = 4
    QA = 5
    RECOVERY = 6  # For existing projects


class VibeCodingAgency:
    """Main orchestrator for the agency framework"""

    def __init__(self):
        self.framework_dir = Path(__file__).parent / "Masterframework"
        self.projects_dir = Path(__file__).parent / "projects"
        self.projects_dir.mkdir(exist_ok=True)

        self.current_project = None
        self.current_phase = None
        self.project_type = None

    def start(self):
        """Main entry point"""
        print("\n" + "="*60)
        print("🏢 VIBE CODING AGENCY")
        print("Structured Software Project Management")
        print("="*60 + "\n")

        # Step 1: Classify project
        self.classify_project()

        # Step 2: Get project name
        self.get_project_name()

        # Step 3: Create project state
        self.create_project_state()

        # Step 4: Load templates and start phases
        self.run_phase_sequence()

    def classify_project(self):
        """Ask user: NEW or EXISTING project?"""
        print("Is this a NEW project or EXISTING project?\n")
        print("A) NEW project (no existing code)")
        print("B) EXISTING project (has codebase that needs work)\n")

        choice = input("Enter A or B: ").strip().upper()

        if choice == "A":
            self.project_type = ProjectType.NEW
            print("\n✓ Type: NEW PROJECT")
            print("  Flow: INTAKE → ARCHITECTURE → IMPLEMENTATION → CODE → QA\n")
        elif choice == "B":
            self.project_type = ProjectType.EXISTING
            print("\n✓ Type: EXISTING PROJECT")
            print("  Flow: RECOVERY → (ARCHITECTURE) → IMPLEMENTATION → CODE → QA\n")
        else:
            print("Invalid choice. Try again.")
            self.classify_project()

    def get_project_name(self):
        """Get project name from user"""
        name = input("Project name? ").strip()

        if not name:
            print("Project name required.")
            self.get_project_name()
            return

        self.current_project = name
        print(f"\n✓ Project: {name}\n")

    def create_project_state(self):
        """Create project directory and state file"""
        project_dir = self.projects_dir / self.current_project
        project_dir.mkdir(exist_ok=True)

        state_file = project_dir / "state.json"

        if not state_file.exists():
            state = {
                "project_name": self.current_project,
                "project_type": self.project_type.value,
                "created_at": datetime.now().isoformat(),
                "current_phase": None,
                "completed_phases": [],
                "artifacts": {}
            }
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
            print(f"✓ Project state created: {project_dir}\n")
        else:
            print(f"✓ Project state loaded: {project_dir}\n")

    def run_phase_sequence(self):
        """Execute phase sequence based on project type"""
        if self.project_type == ProjectType.NEW:
            phases = [
                Phase.INTAKE,
                Phase.ARCHITECTURE,
                Phase.IMPLEMENTATION,
                Phase.CODE_GENERATION,
                Phase.QA
            ]
        else:
            phases = [
                Phase.RECOVERY,
                Phase.IMPLEMENTATION,
                Phase.CODE_GENERATION,
                Phase.QA
            ]

        for phase in phases:
            self.execute_phase(phase)

            # Ask to proceed
            if phase != phases[-1]:  # Not the last phase
                proceed = input(f"\nProceed to next phase? (y/n): ").strip().lower()
                if proceed != "y":
                    print("Stopping here. You can resume later.")
                    self.save_state()
                    sys.exit(0)

        print("\n" + "="*60)
        print("✓ PROJECT COMPLETE")
        print("="*60)
        self.save_state()

    def execute_phase(self, phase: Phase):
        """Execute a single phase"""
        print("\n" + "-"*60)
        print(f"PHASE {phase.value}: {phase.name}")
        print("-"*60 + "\n")

        # Load template
        template_file = self.get_template_file(phase)
        if template_file:
            print(f"📋 Template: {template_file.name}\n")
            self.show_phase_instructions(template_file)
        else:
            print(f"⚠ Template not found for phase {phase.name}\n")

        # Collect phase information
        self.collect_phase_input(phase)

        # Mark phase as complete
        self.current_phase = phase

    def get_template_file(self, phase: Phase) -> Path:
        """Get template markdown file for phase"""
        template_mapping = {
            Phase.INTAKE: "02.md",
            Phase.ARCHITECTURE: "04.md",
            Phase.IMPLEMENTATION: "05.md",
            Phase.CODE_GENERATION: "06.md",
            Phase.QA: "07.md",
            Phase.RECOVERY: "03.md",
        }

        filename = template_mapping.get(phase)
        if filename:
            filepath = self.framework_dir / filename
            if filepath.exists():
                return filepath

        return None

    def show_phase_instructions(self, template_file: Path):
        """Show first 50 lines of template to guide user"""
        with open(template_file, "r") as f:
            lines = f.readlines()[:40]
            print("".join(lines))
        print("\n[... full template available in framework]\n")

    def collect_phase_input(self, phase: Phase):
        """Collect user input for phase"""
        input_prompt = {
            Phase.INTAKE: "Describe your project (problem, solution, users, scope): ",
            Phase.RECOVERY: "Describe current state of codebase: ",
            Phase.ARCHITECTURE: "Ready to design architecture (y/n)? ",
            Phase.IMPLEMENTATION: "Ready to create implementation plan (y/n)? ",
            Phase.CODE_GENERATION: "Ready to generate code (y/n)? ",
            Phase.QA: "Ready for quality assurance (y/n)? ",
        }

        prompt = input_prompt.get(phase, "Continue (y/n)? ")

        if phase in [Phase.INTAKE, Phase.RECOVERY]:
            user_input = input(f"\n{prompt}: ").strip()
            if user_input:
                self.save_artifact(phase, "input", user_input)
        else:
            response = input(f"\n{prompt}: ").strip().lower()
            if response != "y":
                print(f"Skipping {phase.name}")
                return

        print(f"✓ {phase.name} input recorded")

    def save_artifact(self, phase: Phase, artifact_type: str, content: str):
        """Save artifact to project state"""
        project_dir = self.projects_dir / self.current_project
        state_file = project_dir / "state.json"

        with open(state_file, "r") as f:
            state = json.load(f)

        if phase.name not in state["artifacts"]:
            state["artifacts"][phase.name] = {}

        state["artifacts"][phase.name][artifact_type] = content
        state["completed_phases"].append(phase.name)

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    def save_state(self):
        """Save current state"""
        project_dir = self.projects_dir / self.current_project
        state_file = project_dir / "state.json"

        with open(state_file, "r") as f:
            state = json.load(f)

        if self.current_phase:
            state["current_phase"] = self.current_phase.name

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)


def main():
    """Entry point"""
    try:
        agency = VibeCodingAgency()
        agency.start()
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
