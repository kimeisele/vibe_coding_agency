import click
from cli.commands import new, research, scan, report, status

@click.group()
def cli():
    """
    Agency CLI - A research-first, data-driven consulting tool.
    
    This CLI helps you follow a structured protocol for software analysis,
    ensuring all findings are backed by research and real data.
    """
    pass

# Register commands
cli.add_command(new.new)
cli.add_command(research.research)
cli.add_command(scan.scan)
cli.add_command(report.report)
cli.add_command(status.status)
