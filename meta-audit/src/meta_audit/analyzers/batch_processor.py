"""
Batch Processor for analyzing multiple ProjectCapsule files.

Enables offline analysis of project snapshots without access to original source code.
Maintains isolation between projects and aggregates results.
"""

import json
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from meta_audit.core.models import ProjectCapsule, AnalysisResult
from meta_audit.analyzers.collectors import run_all_collectors

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Process multiple ProjectCapsule files in batch mode."""

    @staticmethod
    def discover_capsules(directory_path: str) -> List[Path]:
        """
        Find all *.capsule.json files in a directory.

        Args:
            directory_path: Directory to search

        Returns:
            List of Path objects for capsule files
        """
        dir_path = Path(directory_path)

        if not dir_path.is_dir():
            logger.error(f"Directory does not exist: {directory_path}")
            return []

        capsule_files = sorted(dir_path.glob("*.capsule.json"))

        logger.info(f"Discovered {len(capsule_files)} capsule files in {directory_path}")
        return capsule_files

    @staticmethod
    def load_capsule(capsule_path: str) -> Optional[ProjectCapsule]:
        """
        Load a ProjectCapsule from JSON file.

        Args:
            capsule_path: Path to capsule JSON file

        Returns:
            ProjectCapsule object or None if loading failed
        """
        try:
            capsule_file = Path(capsule_path)

            if not capsule_file.exists():
                logger.error(f"Capsule file not found: {capsule_path}")
                return None

            with open(capsule_file, "r", encoding="utf-8") as f:
                capsule_data = json.load(f)

            # Use Pydantic to validate and load the capsule
            capsule = ProjectCapsule(**capsule_data)

            logger.info(f"Loaded capsule: {capsule.project_name} ({len(capsule.files)} files)")
            return capsule

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in capsule file {capsule_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load capsule {capsule_path}: {e}")
            return None

    @staticmethod
    def analyze_capsule(capsule: ProjectCapsule) -> Dict[str, Any]:
        """
        Run all collectors on a ProjectCapsule's file contents.

        Creates temporary project structure from capsule and analyzes it.
        Results include the capsule metadata.

        Args:
            capsule: ProjectCapsule to analyze

        Returns:
            Dictionary with:
            - project_name: Name of the project
            - capsule_created_at: When the capsule was created
            - files_count: Number of files in capsule
            - collectors_data: Results from all collectors
            - all_findings: Flattened list of all AnalysisResult objects
            - errors: Any errors during analysis
            - status: "success" or "partial_success"
        """
        try:
            logger.info(f"Analyzing capsule: {capsule.project_name}")

            # Create temporary directory for analysis
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)

                # Write all capsule files to temporary directory
                for capsule_file in capsule.files:
                    file_path = tmpdir_path / capsule_file.path
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    if capsule_file.content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(capsule_file.content)

                logger.info(f"Extracted {len(capsule.files)} files to temporary directory")

                # Run collectors on the temporary directory
                result = run_all_collectors(str(tmpdir_path))

                # Enhance result with capsule metadata
                result["project_name"] = capsule.project_name
                result["capsule_created_at"] = capsule.created_at.isoformat()
                result["files_count"] = capsule.files_count

                return result

        except Exception as e:
            logger.error(f"Failed to analyze capsule {capsule.project_name}: {e}")
            return {
                "project_name": capsule.project_name,
                "error": str(e),
                "status": "failed",
            }

    @staticmethod
    def analyze_capsules_parallel(
        capsules: List[ProjectCapsule], max_workers: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze multiple capsules in parallel.

        Args:
            capsules: List of ProjectCapsule objects
            max_workers: Maximum number of parallel workers

        Returns:
            Dictionary mapping project_name → analysis result
        """
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all analysis tasks
            futures = {
                executor.submit(BatchProcessor.analyze_capsule, capsule): capsule.project_name
                for capsule in capsules
            }

            # Collect results as they complete
            for future in as_completed(futures):
                project_name = futures[future]
                try:
                    result = future.result()
                    results[project_name] = result
                    logger.info(f"✓ Analysis complete for {project_name}")
                except Exception as e:
                    logger.error(f"Analysis failed for {project_name}: {e}")
                    results[project_name] = {
                        "project_name": project_name,
                        "error": str(e),
                        "status": "failed",
                    }

        return results

    @staticmethod
    def flatten_all_findings(
        analysis_results: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Flatten all findings from multiple project analyses.

        Adds project_name to each finding for tracking.

        Args:
            analysis_results: Dict of project_name → analysis result

        Returns:
            Flattened list of all findings with project attribution
        """
        all_findings = []

        for project_name, result in analysis_results.items():
            if "error" in result:
                logger.warning(f"Skipping failed project {project_name}")
                continue

            all_findings_list = result.get("all_findings", [])

            for finding in all_findings_list:
                # Convert AnalysisResult to dict if needed
                if isinstance(finding, AnalysisResult):
                    finding_dict = finding.model_dump(mode="json")
                else:
                    finding_dict = finding

                # Add project attribution
                finding_dict["project"] = project_name
                all_findings.append(finding_dict)

        logger.info(f"Flattened {len(all_findings)} findings from {len(analysis_results)} projects")
        return all_findings
