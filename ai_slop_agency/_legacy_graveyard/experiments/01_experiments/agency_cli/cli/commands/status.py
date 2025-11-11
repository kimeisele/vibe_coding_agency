import click
from core.reporter import get_project_status

@click.command()
@click.argument('project_name')
def status(project_name: str):
    """Checks the completion status of a project's protocols."""
    try:
        project_status = get_project_status(project_name)
        click.echo(f"📊 Status for project: '{project_name}'\n")
        for filename, status_text in project_status.items():
            if "Complete" in status_text:
                color = "green"
                icon = "✅"
            elif "In progress" in status_text:
                color = "yellow"
                icon = "⚠️"
            else:
                color = "red"
                icon = "❌"
            click.secho(f"{icon} {filename}: {status_text}", fg=color)
            
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ An unexpected error occurred: {e}", err=True)
