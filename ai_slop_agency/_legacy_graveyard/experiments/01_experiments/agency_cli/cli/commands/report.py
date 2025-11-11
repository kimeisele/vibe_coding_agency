import click
from datetime import datetime

from core.reporter import generate_report_template
from config.settings import PROJECTS_DIR

@click.command()
@click.argument('project_name')
def report(project_name: str):
    """Generates a report by assembling the project's protocols."""
    click.echo(f"📄 Generating report for: {project_name}")
    
    try:
        report_content, all_passed = generate_report_template(project_name)
        
        if not all_passed:
            click.secho("\n⚠️  VALIDATION FAILED!", fg="yellow")
            click.echo("   The protocols are not fully filled out or contain speculation.")
            if not click.confirm("Generate incomplete report anyway?"):
                return
        
        report_dir = PROJECTS_DIR / project_name / "reports"
        report_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d')
        report_file = report_dir / f"report_{ts}.md"
        
        report_file.write_text(report_content)
        
        click.secho(f"\n✅ Report template generated: {report_file}", fg="green")
        click.echo("\n📝 FINAL STEPS (HUMAN):")
        click.echo("1. Open the report and fill in the [HUMAN: ...] sections.")
        click.echo("2. Write the Executive Summary and Recommendations.")
        click.echo("3. Review for client-readiness.")

    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ An unexpected error occurred: {e}", err=True)
