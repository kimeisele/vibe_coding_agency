"""
Central Reporter module for consistent CLI output formatting.

This module provides standardized functions for all user-facing messages
to ensure consistency across the toolkit and eliminate "AI slop" inconsistencies.
"""

import json

import typer
from rich.console import Console


class Reporter:
    """Centralized reporter for consistent CLI output formatting."""

    def __init__(self, json_output: bool = False):
        """Initialize reporter.

        Args:
            json_output: If True, output JSON format instead of human-readable
        """
        self.json_output = json_output
        self.console = Console()

    def success(self, message: str, data: dict | None = None) -> None:
        """Display success message.

        Args:
            message: Success message to display
            data: Optional data to include in JSON output
        """
        if self.json_output:
            output = {"status": "success", "message": message}
            if data:
                output.update(data)
            print(json.dumps(output))
        else:
            typer.secho(f"✓ {message}", fg="green")

    def error(self, message: str, data: dict | None = None, exit_code: int = 1) -> None:
        """Display error message and exit.

        Args:
            message: Error message to display
            data: Optional data to include in JSON output
            exit_code: Exit code for typer.Exit
        """
        if self.json_output:
            output = {"status": "error", "message": message}
            if data:
                output.update(data)
            print(json.dumps(output))
        else:
            typer.secho(f"✗ Error: {message}", fg="red")
        raise typer.Exit(exit_code)

    def warning(self, message: str, data: dict | None = None) -> None:
        """Display warning message.

        Args:
            message: Warning message to display
            data: Optional data to include in JSON output
        """
        if self.json_output:
            output = {"status": "warning", "message": message}
            if data:
                output.update(data)
            print(json.dumps(output))
        else:
            typer.secho(f"⚠ {message}", fg="yellow")

    def info(self, message: str, data: dict | None = None) -> None:
        """Display info message.

        Args:
            message: Info message to display
            data: Optional data to include in JSON output
        """
        if self.json_output:
            output = {"status": "info", "message": message}
            if data:
                output.update(data)
            print(json.dumps(output))
        else:
            typer.echo(message)

    def processing(self, message: str) -> None:
        """Display processing/working message.

        Args:
            message: Processing message to display
        """
        if not self.json_output:
            typer.echo(message)

    def dry_run(self, message: str) -> None:
        """Display dry run message.

        Args:
            message: Dry run message to display
        """
        if self.json_output:
            print(json.dumps({"status": "dry_run", "message": message}))
        else:
            typer.echo(f"[DRY RUN] {message}")

    def cost(self, cost: float, provider: str | None = None) -> None:
        """Display cost information.

        Args:
            cost: Cost amount
            provider: Optional provider name
        """
        if self.json_output:
            output = {"cost": round(cost, 4)}
            if provider:
                output["provider"] = provider
            print(json.dumps(output))
        else:
            typer.secho(f"💰 Total cost: ${cost:.4f}", fg="cyan")
            if provider:
                typer.secho(f"🔌 Provider: {provider}", fg="cyan")

    def batch_summary(self, total: int, successful: int, failed: int = 0) -> None:
        """Display batch processing summary.

        Args:
            total: Total items processed
            successful: Number of successful items
            failed: Number of failed items
        """
        if self.json_output:
            print(
                json.dumps(
                    {
                        "status": "success",
                        "total": total,
                        "successful": successful,
                        "failed": failed,
                    }
                )
            )
        else:
            typer.echo("")
            typer.secho("✓ Batch complete:", fg="green")
            typer.echo(f"  Total: {total}")
            typer.secho(f"  Successful: {successful}", fg="green")
            if failed > 0:
                typer.secho(f"  Failed: {failed}", fg="red")

    def validation_result(
        self, filename: str, passed: bool, reason: str | None = None
    ) -> None:
        """Display validation result.

        Args:
            filename: Name of the file being validated
            passed: Whether validation passed
            reason: Optional reason for failure
        """
        if self.json_output:
            output = {"file": filename, "passed": passed}
            if reason:
                output["reason"] = reason
            print(json.dumps(output))
        else:
            if passed:
                typer.secho(f"  ✓ {filename}: PASSED", fg="green")
                if reason:
                    typer.echo(f"    ({reason})")
            else:
                typer.secho(f"  ✗ {filename}: FAILED", fg="red")
                if reason:
                    typer.echo(f"    ({reason})")

    def header(self, title: str, width: int = 50) -> None:
        """Display section header.

        Args:
            title: Header title
            width: Width of the header line
        """
        if not self.json_output:
            line = "=" * width
            typer.secho(line, fg="blue")
            typer.secho(title, fg="blue")
            typer.secho(line, fg="blue")

    def section(self, title: str) -> None:
        """Display section title.

        Args:
            title: Section title
        """
        if not self.json_output:
            typer.secho(f"\n{title}", fg="green")

    def list_item(
        self, item: str, description: str | None = None, indent: int = 2
    ) -> None:
        """Display list item.

        Args:
            item: List item text
            description: Optional description
            indent: Number of spaces to indent
        """
        if not self.json_output:
            prefix = " " * indent
            if description:
                typer.echo(f"{prefix}{item:<30} {description}")
            else:
                typer.echo(f"{prefix}{item}")

    def divider(self, width: int = 60) -> None:
        """Display divider line.

        Args:
            width: Width of the divider
        """
        if not self.json_output:
            typer.echo(f"{'=' * width}")


# Global reporter instance that can be configured
_reporter: Reporter | None = None


def get_reporter(json_output: bool = False) -> Reporter:
    """Get or create the global reporter instance.

    Args:
        json_output: Whether to output JSON format

    Returns:
        Reporter instance
    """
    global _reporter
    if _reporter is None or _reporter.json_output != json_output:
        _reporter = Reporter(json_output)
    return _reporter


def configure_reporter(json_output: bool = False) -> None:
    """Configure the global reporter.

    Args:
        json_output: Whether to output JSON format
    """
    global _reporter
    _reporter = Reporter(json_output)
