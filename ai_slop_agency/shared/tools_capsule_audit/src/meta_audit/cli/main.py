"""
Main CLI entry point for the Meta Audit tool.
"""
import click

from meta_audit.cli.commands.analyze import analyze
from meta_audit.cli.commands.capsule import create as capsule_create, show as capsule_show


@click.group()
def cli():
    """
    Meta Audit Tool - A comprehensive code analysis and improvement tool.

    Commands:
      analyze   Run analysis on a project or corpus
      capsule   Manage ProjectCapsule snapshots
    """
    pass


# Main commands
cli.add_command(analyze)

# Capsule command group
@cli.group()
def capsule():
    """
    Manage ProjectCapsule snapshots for offline analysis.

    ProjectCapsules are JSON snapshots of projects that can be analyzed
    without access to the original source code.
    """
    pass


# Capsule subcommands
capsule.add_command(capsule_create, name="create")
capsule.add_command(capsule_show, name="show")


if __name__ == "__main__":
    cli()
