"""
State Manager - Persistent state across KDAF phases

Purpose: Track progress through phases, store outputs, enable resume
Philosophy: State is truth. If it's not in state.json, it didn't happen.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

class PhaseStatus(Enum):
    """Phase execution status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class ConfidenceLevel(Enum):
    """Confidence in findings (based on data availability)"""
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"        # 1 source or tool
    MEDIUM = "MEDIUM"  # 2-3 sources or tools
    HIGH = "HIGH"      # 3+ sources + tools

class StateManager:
    """
    Manages project state across KDAF phases.

    State Schema:
    {
        "project_id": "unique_id",
        "client": "client_name",
        "project_name": "project_name",
        "created_at": "ISO timestamp",
        "last_updated": "ISO timestamp",
        "phases": {
            "1_understand": {
                "status": "COMPLETE",
                "started_at": "ISO timestamp",
                "completed_at": "ISO timestamp",
                "outputs": {
                    "facts": [...],
                    "knowledge_gaps": [...],
                    "validation_questions": [...]
                }
            },
            "2_research": {
                "status": "COMPLETE",
                "outputs": {
                    "sources": [...],
                    "tools_identified": ["flake8", "bandit"],
                    "best_practices": [...]
                }
            },
            "3_validate": {
                "status": "IN_PROGRESS",
                "outputs": {
                    "tool_results": {
                        "flake8": "path/to/output",
                        "bandit": "path/to/output"
                    },
                    "findings": [...]
                }
            },
            "4_report": {
                "status": "PENDING"
            }
        },
        "confidence": "UNKNOWN",
        "next_action": "Phase 2: Research"
    }
    """

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.state_file = self.project_path / "state.json"
        self.state = self._load_or_create()

    def _load_or_create(self) -> Dict[str, Any]:
        """Load existing state or create new"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        else:
            return self._create_initial_state()

    def _create_initial_state(self) -> Dict[str, Any]:
        """Create initial state structure"""
        project_name = self.project_path.name
        client_name = self.project_path.parent.name.replace('client_', '')

        return {
            "project_id": f"{client_name}_{project_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "client": client_name,
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "phases": {
                "1_understand": {
                    "status": PhaseStatus.PENDING.value,
                    "outputs": {}
                },
                "2_research": {
                    "status": PhaseStatus.PENDING.value,
                    "outputs": {}
                },
                "3_validate": {
                    "status": PhaseStatus.PENDING.value,
                    "outputs": {}
                },
                "4_report": {
                    "status": PhaseStatus.PENDING.value,
                    "outputs": {}
                }
            },
            "confidence": ConfidenceLevel.UNKNOWN.value,
            "next_action": "Phase 1: Semantic Understanding"
        }

    def save(self):
        """Persist state to disk"""
        self.state["last_updated"] = datetime.now().isoformat()

        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def update_phase(self, phase: str, status: PhaseStatus, outputs: Optional[Dict] = None):
        """Update phase status and outputs"""
        phase_key = f"{phase}_" + {
            "1": "understand",
            "2": "research",
            "3": "validate",
            "4": "report"
        }[phase]

        if phase_key not in self.state["phases"]:
            raise ValueError(f"Invalid phase: {phase}")

        # Update status
        self.state["phases"][phase_key]["status"] = status.value

        # Update timestamps
        if status == PhaseStatus.IN_PROGRESS:
            self.state["phases"][phase_key]["started_at"] = datetime.now().isoformat()
        elif status == PhaseStatus.COMPLETE:
            self.state["phases"][phase_key]["completed_at"] = datetime.now().isoformat()

        # Update outputs
        if outputs:
            self.state["phases"][phase_key]["outputs"].update(outputs)

        # Update next action
        self._update_next_action()

        self.save()

    def _update_next_action(self):
        """Determine next action based on phase statuses"""
        phases = self.state["phases"]

        if phases["1_understand"]["status"] != PhaseStatus.COMPLETE.value:
            self.state["next_action"] = "Phase 1: Semantic Understanding"
        elif phases["2_research"]["status"] != PhaseStatus.COMPLETE.value:
            self.state["next_action"] = "Phase 2: Knowledge Acquisition"
        elif phases["3_validate"]["status"] != PhaseStatus.COMPLETE.value:
            self.state["next_action"] = "Phase 3: Data-Driven Validation"
        elif phases["4_report"]["status"] != PhaseStatus.COMPLETE.value:
            self.state["next_action"] = "Phase 4: Report Generation"
        else:
            self.state["next_action"] = "All phases complete"

    def get_phase_status(self, phase: str) -> str:
        """Get status of specific phase"""
        phase_key = f"{phase}_" + {
            "1": "understand",
            "2": "research",
            "3": "validate",
            "4": "report"
        }[phase]

        return self.state["phases"][phase_key]["status"]

    def get_phase_outputs(self, phase: str) -> Dict[str, Any]:
        """Get outputs from specific phase"""
        phase_key = f"{phase}_" + {
            "1": "understand",
            "2": "research",
            "3": "validate",
            "4": "report"
        }[phase]

        return self.state["phases"][phase_key]["outputs"]

    def can_run_phase(self, phase: str) -> bool:
        """Check if phase can run (dependencies met)"""
        phase_num = int(phase)

        # Phase 1 can always run
        if phase_num == 1:
            return True

        # Other phases require previous phase complete
        prev_phase = str(phase_num - 1)
        prev_status = self.get_phase_status(prev_phase)

        return prev_status == PhaseStatus.COMPLETE.value

    def calculate_confidence(self) -> ConfidenceLevel:
        """
        Calculate overall confidence based on:
        - Number of sources (Phase 2)
        - Number of tool outputs (Phase 3)
        - Validation coverage
        """
        research_outputs = self.get_phase_outputs("2")
        validate_outputs = self.get_phase_outputs("3")

        source_count = len(research_outputs.get("sources", []))
        tool_count = len(validate_outputs.get("tool_results", {}))

        total_evidence = source_count + tool_count

        if total_evidence >= 5:
            return ConfidenceLevel.HIGH
        elif total_evidence >= 3:
            return ConfidenceLevel.MEDIUM
        elif total_evidence >= 1:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNKNOWN

    def get_summary(self) -> Dict[str, Any]:
        """Get high-level summary of project state"""
        return {
            "project_id": self.state["project_id"],
            "client": self.state["client"],
            "project_name": self.state["project_name"],
            "phase_statuses": {
                phase: data["status"]
                for phase, data in self.state["phases"].items()
            },
            "confidence": self.state["confidence"],
            "next_action": self.state["next_action"],
            "last_updated": self.state["last_updated"]
        }
