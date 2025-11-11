#!/usr/bin/env python3
"""
Agency Toolkit Deep Analysis Script
Gathers ACTUAL code structure, not speculation.
"""

import json
import subprocess
from pathlib import Path
from typing import Any


def run_command(cmd: list[str], cwd: Path | None = None) -> str:
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd, timeout=30
        )
        return result.stdout
    except Exception as e:
        return f"ERROR: {e}"


def gather_project_structure(root: Path) -> dict[str, Any]:
    """Gather actual project structure."""
    structure = {"root": str(root), "files": {}, "directories": []}

    # Key directories to analyze
    key_dirs = [
        "agency_toolkit/commands",
        "agency_toolkit/core",
        "agency_toolkit/tasks",  # Does this exist?
        "agency_toolkit/providers",
        "registry/seeds",
        "templates",
        "tests",
    ]

    for dir_path in key_dirs:
        full_path = root / dir_path
        if full_path.exists():
            structure["directories"].append(str(dir_path))
            # Count files
            py_files = list(full_path.rglob("*.py"))
            json_files = list(full_path.rglob("*.json"))
            structure["files"][dir_path] = {
                "python": len(py_files),
                "json": len(json_files),
                "file_list": [f.name for f in py_files + json_files],
            }
        else:
            structure["files"][dir_path] = "NOT_EXISTS"

    return structure


def check_existing_infrastructure(root: Path) -> dict[str, Any]:
    """Check what's ACTUALLY set up."""
    infra = {}

    # Pre-commit
    precommit_file = root / ".pre-commit-config.yaml"
    infra["pre_commit"] = {
        "exists": precommit_file.exists(),
        "content": precommit_file.read_text() if precommit_file.exists() else None,
    }

    # Ruff config
    ruff_files = [root / "ruff.toml", root / "pyproject.toml"]
    for f in ruff_files:
        if f.exists():
            infra["ruff_config"] = {"file": str(f.name), "content": f.read_text()}
            break

    # Mypy config
    mypy_file = root / "mypy.ini"
    infra["mypy"] = {
        "exists": mypy_file.exists(),
        "content": mypy_file.read_text() if mypy_file.exists() else None,
    }

    # CI/CD
    ci_files = [root / ".github/workflows", root / ".gitlab-ci.yml"]
    for f in ci_files:
        if f.exists():
            if f.is_dir():
                infra["ci_cd"] = {
                    "type": "github_actions",
                    "workflows": [wf.name for wf in f.glob("*.yml")],
                }
            else:
                infra["ci_cd"] = {"type": "gitlab", "file": f.name}

    return infra


def analyze_task_handlers(root: Path) -> dict[str, Any]:
    """Analyze ACTUAL task handler implementation."""
    analysis = {}

    # Check if tasks/ directory exists (new structure)
    tasks_dir = root / "agency_toolkit/tasks"
    analysis["new_structure_exists"] = tasks_dir.exists()

    if tasks_dir.exists():
        analysis["new_structure"] = {
            "files": [f.name for f in tasks_dir.glob("*.py")],
            "has_base": (tasks_dir / "base.py").exists(),
            "has_registry": (tasks_dir / "registry.py").exists(),
        }

    # Check old task_handlers.py
    old_file = root / "agency_toolkit/core/task_handlers.py"
    analysis["old_structure_exists"] = old_file.exists()

    if old_file.exists():
        content = old_file.read_text()
        analysis["old_structure"] = {
            "lines": len(content.splitlines()),
            "has_task_registry": "TASK_REGISTRY" in content,
            "handler_count": content.count("def handle_"),
        }

    return analysis


def analyze_orchestrator(root: Path) -> dict[str, Any]:
    """Analyze orchestrator.py implementation."""
    orchestrator_file = root / "agency_toolkit/core/orchestrator.py"

    if not orchestrator_file.exists():
        return {"exists": False}

    content = orchestrator_file.read_text()
    lines = content.splitlines()

    return {
        "exists": True,
        "lines": len(lines),
        "imports": [
            line.strip()
            for line in lines[:30]
            if line.strip().startswith(("import ", "from "))
        ],
        "has_execute_module": "def execute_module" in content,
        "has_format_task_params": "def _format_task_params" in content,
        "uses_task_registry": "TASK_REGISTRY" in content,
        "uses_get_task_handler": "get_task_handler" in content,
    }


def analyze_complexity_hotspots(root: Path) -> dict[str, Any]:
    """Find actual high-complexity functions."""
    try:
        # Run radon cc
        output = run_command(
            ["radon", "cc", str(root / "agency_toolkit"), "-a", "-s"], cwd=root
        )

        # Parse output for CC >= 10
        hotspots = []
        for line in output.splitlines():
            if " - " in line:
                parts = line.split(" - ")
                if len(parts) >= 2:
                    # Extract CC score
                    score_part = parts[1].strip()
                    if "(" in score_part:
                        try:
                            cc = int(score_part.split("(")[1].split(")")[0])
                            if cc >= 10:
                                hotspots.append(
                                    {"location": parts[0].strip(), "score": cc}
                                )
                        except:
                            pass

        return {
            "found": len(hotspots),
            "hotspots": sorted(hotspots, key=lambda x: x["score"], reverse=True)[:10],
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_registry_files(root: Path) -> dict[str, Any]:
    """Analyze actual registry JSON structure."""
    registry_dir = root / "registry/seeds"

    if not registry_dir.exists():
        return {"exists": False}

    analysis = {"exists": True, "files": {}}

    for json_file in registry_dir.glob("*.json"):
        try:
            data = json.loads(json_file.read_text())
            analysis["files"][json_file.name] = {
                "keys": list(data.keys()) if isinstance(data, dict) else "not_dict",
                "size_kb": json_file.stat().st_size / 1024,
                "top_level_count": len(data) if isinstance(data, (dict, list)) else 0,
            }

            # Specific analysis for solutions.json
            if json_file.name == "solutions.json":
                if isinstance(data, list):
                    analysis["solutions_structure"] = {
                        "count": len(data),
                        "sample_keys": list(data[0].keys()) if data else [],
                        "has_modules": any("module" in s for s in data)
                        if data
                        else False,
                    }
        except Exception as e:
            analysis["files"][json_file.name] = {"error": str(e)}

    return analysis


def check_test_suite(root: Path) -> dict[str, Any]:
    """Analyze test structure."""
    tests_dir = root / "tests"

    if not tests_dir.exists():
        return {"exists": False}

    test_files = list(tests_dir.rglob("test_*.py"))

    analysis = {
        "exists": True,
        "test_files": [f.relative_to(tests_dir).as_posix() for f in test_files],
        "count": len(test_files),
    }

    # Check if tests run
    try:
        result = run_command(["pytest", "--collect-only", "-q"], cwd=root)
        analysis["pytest_works"] = "error" not in result.lower()
        analysis["test_count"] = result.count("test_")
    except:
        analysis["pytest_works"] = False

    return analysis


def main():
    """Run all analysis."""
    print("🔍 Agency Toolkit Deep Analysis\n")
    print("=" * 60)

    # Assume we're in project root
    root = Path.cwd()

    # Verify this is the right project
    if not (root / "agency_toolkit").exists():
        print("❌ ERROR: Not in agency_toolkit root directory")
        print(f"Current dir: {root}")
        return

    report = {
        "project_root": str(root),
        "structure": gather_project_structure(root),
        "infrastructure": check_existing_infrastructure(root),
        "task_handlers": analyze_task_handlers(root),
        "orchestrator": analyze_orchestrator(root),
        "complexity": analyze_complexity_hotspots(root),
        "registry": analyze_registry_files(root),
        "tests": check_test_suite(root),
    }

    # Save report
    report_file = root / "analysis_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Analysis complete. Report saved to: {report_file}")
    print("\n📊 Quick Summary:")
    print(f"  - Pre-commit exists: {report['infrastructure']['pre_commit']['exists']}")
    print(
        f"  - New task structure exists: {report['task_handlers']['new_structure_exists']}"
    )
    print(
        f"  - Old task_handlers exists: {report['task_handlers']['old_structure_exists']}"
    )
    print(f"  - Complexity hotspots: {report['complexity'].get('found', 'unknown')}")
    print(f"  - Test files: {report['tests'].get('count', 0)}")

    return report


if __name__ == "__main__":
    main()
