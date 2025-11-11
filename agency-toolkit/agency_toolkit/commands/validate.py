"""Snapshot validation and regression testing command."""

import hashlib
import json
import logging
import shutil
from pathlib import Path

import typer

from agency_toolkit.core.reporter import get_reporter

logger = logging.getLogger(__name__)

validate_command = typer.Typer(help="Validate outputs against approved snapshots")


def _hash_file(file_path: Path) -> str:
    """Calculate SHA-256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def _extract_pdf_text(pdf_path: Path, reporter=None) -> str:
    """Extract text from PDF for comparison."""
    if reporter is None:
        reporter = get_reporter()

    try:
        from pypdf import PdfReader

        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except ImportError:
        reporter.warning("⚠ pypdf not installed. Install with: pip install pypdf")
        return ""


def _compare_pdf_files(
    current_file: Path, approved_file: Path, filename: str, reporter=None
) -> dict:
    """Compare two PDF files by text content.

    Returns:
        Result dict with status and details
    """
    if reporter is None:
        reporter = get_reporter()

    current_text = _extract_pdf_text(current_file, reporter)
    approved_text = _extract_pdf_text(approved_file, reporter)

    if current_text == approved_text:
        reporter.validation_result(filename, True, "text match")
        return {"passed": True}
    else:
        reporter.validation_result(filename, False, "text differs")
        return {
            "passed": False,
            "difference": {"file": filename, "status": "different", "type": "pdf_text"},
        }


def _compare_image_files(
    current_file: Path, approved_file: Path, filename: str, reporter=None
) -> dict:
    """Compare two image files by hash.

    Returns:
        Result dict with status and details
    """
    if reporter is None:
        reporter = get_reporter()

    current_hash = _hash_file(current_file)
    approved_hash = _hash_file(approved_file)

    if current_hash == approved_hash:
        reporter.validation_result(filename, True, "hash match")
        return {"passed": True}
    else:
        reporter.validation_result(filename, False, "hash differs")
        return {
            "passed": False,
            "difference": {
                "file": filename,
                "status": "different",
                "type": "image_hash",
                "current_hash": current_hash,
                "approved_hash": approved_hash,
            },
        }


def _compare_json_files(
    current_file: Path, approved_file: Path, filename: str, reporter=None
) -> dict:
    """Compare two JSON files by content.

    Returns:
        Result dict with status and details
    """
    if reporter is None:
        reporter = get_reporter()

    with open(current_file) as f:
        current_data = json.load(f)
    with open(approved_file) as f:
        approved_data = json.load(f)

    if current_data == approved_data:
        reporter.validation_result(filename, True, "content match")
        return {"passed": True}
    else:
        reporter.validation_result(filename, False, "content differs")
        return {
            "passed": False,
            "difference": {
                "file": filename,
                "status": "different",
                "type": "json_content",
            },
        }


def _compare_generic_files(
    current_file: Path, approved_file: Path, filename: str, reporter=None
) -> dict:
    """Compare two files by hash.

    Returns:
        Result dict with status and details
    """
    if reporter is None:
        reporter = get_reporter()

    current_hash = _hash_file(current_file)
    approved_hash = _hash_file(approved_file)

    if current_hash == approved_hash:
        reporter.validation_result(filename, True, "hash match")
        return {"passed": True}
    else:
        reporter.validation_result(filename, False, "hash differs")
        return {
            "passed": False,
            "difference": {
                "file": filename,
                "status": "different",
                "type": "file_hash",
            },
        }


def _get_file_comparator(filename: str):
    """Get the appropriate comparator function for a file type.

    Args:
        filename: Name of file to compare

    Returns:
        Comparator function (current, approved, filename) -> dict
    """
    if filename.endswith(".pdf"):
        return _compare_pdf_files
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        return _compare_image_files
    elif filename.endswith(".json"):
        return _compare_json_files
    else:
        return _compare_generic_files


def _process_file_comparison(
    filename: str, current_files: dict, approved_files: dict, reporter=None
) -> dict:
    """Process a single file comparison.

    Returns:
        Dict with passed (bool) and optional difference info
    """
    if reporter is None:
        reporter = get_reporter()

    if filename not in approved_files:
        reporter.validation_result(filename, False, "NEW (not in approved)")
        return {
            "passed": False,
            "status": "new",
            "difference": {"file": filename, "status": "new"},
        }

    if filename not in current_files:
        reporter.validation_result(
            filename, False, "MISSING (in approved but not generated)"
        )
        return {
            "passed": False,
            "status": "missing",
            "difference": {"file": filename, "status": "missing"},
        }

    comparator = _get_file_comparator(filename)
    result = comparator(
        current_files[filename], approved_files[filename], filename, reporter
    )
    result["status"] = "compared"
    return result


def _validate_snapshot_dirs(
    current_dir: Path, approved_dir: Path, reporter=None
) -> bool:
    """Check if snapshot directories exist."""
    if reporter is None:
        reporter = get_reporter()

    if not current_dir.exists():
        reporter.error(f"✗ Current snapshot directory not found: {current_dir}")
        return False
    if not approved_dir.exists():
        reporter.warning(f"✗ Approved snapshot directory not found: {approved_dir}")
        reporter.warning("  Run with --approve to create initial snapshots")
        return False
    return True


def _collect_snapshot_files(
    current_dir: Path, approved_dir: Path
) -> tuple[dict, dict, set]:
    """Collect and organize snapshot files from both directories.

    Returns:
        Tuple of (current_files, approved_files, all_filenames)
    """
    current_files = {f.name: f for f in current_dir.glob("*") if f.is_file()}
    approved_files = {f.name: f for f in approved_dir.glob("*") if f.is_file()}
    all_files = set(current_files.keys()) | set(approved_files.keys())
    return current_files, approved_files, all_files


def _aggregate_comparison_results(results: list[dict]) -> dict:
    """Aggregate results from individual file comparisons.

    Args:
        results: List of comparison result dictionaries

    Returns:
        Aggregated results dict with counts and differences
    """
    aggregated = {
        "total": len(results),
        "passed": 0,
        "failed": 0,
        "missing": 0,
        "differences": [],
    }

    for result in results:
        if result["passed"]:
            aggregated["passed"] += 1
        else:
            if result["status"] == "new":
                aggregated["missing"] += 1
            else:
                aggregated["failed"] += 1
            aggregated["differences"].append(result["difference"])

    return aggregated


def _compare_snapshots(current_dir: Path, approved_dir: Path, reporter=None) -> dict:
    """Compare current snapshots against approved (orchestrator function).

    Returns:
        Results dict with total, passed, failed, missing counts and differences list
    """
    if reporter is None:
        reporter = get_reporter()

    # Initialize empty results for invalid directories
    empty_results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "missing": 0,
        "differences": [],
    }

    if not _validate_snapshot_dirs(current_dir, approved_dir, reporter):
        return empty_results

    # Collect files from both directories
    current_files, approved_files, all_files = _collect_snapshot_files(
        current_dir, approved_dir
    )

    # Process each file comparison
    comparison_results = []
    for filename in sorted(all_files):
        result = _process_file_comparison(
            filename, current_files, approved_files, reporter
        )
        comparison_results.append(result)

    # Aggregate and return results
    return _aggregate_comparison_results(comparison_results)


@validate_command.command(name="snapshot")
def snapshot_validate(
    ctx: typer.Context,
    approve: bool = typer.Option(
        False, "--approve", help="Approve current snapshots as new baseline"
    ),
    generate: bool = typer.Option(
        False, "--generate", help="Generate snapshots before validation"
    ),
) -> None:
    """Validate outputs against approved snapshots.

    Examples:
        toolkit validate snapshot          # Compare against approved
        toolkit validate snapshot --generate   # Generate then compare
        toolkit validate snapshot --approve    # Promote current to approved
    """
    config = ctx.obj
    reporter = get_reporter(config.json_output)

    snapshots_dir = Path("snapshots")
    current_dir = snapshots_dir / "current"
    approved_dir = snapshots_dir / "approved"

    # Ensure directories exist
    current_dir.mkdir(parents=True, exist_ok=True)
    approved_dir.mkdir(parents=True, exist_ok=True)

    if approve:
        # Promote current to approved
        if not current_dir.exists() or not any(current_dir.iterdir()):
            reporter.error("No current snapshots to approve")

        reporter.processing(f"📦 Promoting {current_dir} to {approved_dir}...")

        # Clear approved and copy current
        for file in approved_dir.glob("*"):
            if file.is_file():
                file.unlink()

        for file in current_dir.glob("*"):
            if file.is_file():
                shutil.copy2(file, approved_dir / file.name)
                reporter.success(f"Approved: {file.name}")

        reporter.success("Snapshots approved")
        return

    if generate:
        reporter.processing("🔨 Generating snapshots...")
        reporter.warning("Generation not yet implemented - use commands manually")
        # TODO: Implement automatic generation
        # This would run: briefing, social, structure with fixed inputs

    # Validate
    reporter.info("\n🔍 Validating snapshots...\n")
    results = _compare_snapshots(current_dir, approved_dir, reporter)

    # Summary
    reporter.divider(60)
    reporter.info(f"Total: {results['total']}")

    if results["passed"] > 0:
        reporter.success(f"Passed: {results['passed']}")

    if results["failed"] > 0:
        reporter.error(f"Failed: {results['failed']}", exit_code=0)  # Don't exit yet

    if results["missing"] > 0:
        reporter.warning(f"New/Missing: {results['missing']}")

    reporter.divider(60)

    # Exit status
    if results["failed"] > 0:
        reporter.error("Snapshot validation failed")
    elif results["total"] == 0:
        reporter.warning("No snapshots found to validate")
    else:
        reporter.success("All snapshots validated")
