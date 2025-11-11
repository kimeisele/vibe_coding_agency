import click
from typing import Optional
import json

from core.scanner import run_scan
from config.settings import PROJECTS_DIR


@click.command()
@click.option('--path', 'code_path', required=True, type=click.Path(exists=True, file_okay=False, resolve_path=True),
              help='Absolute path to the codebase to analyze.')
@click.option('--tech', required=True, 
              type=click.Choice(['python', 'javascript', 'django', 'react'], case_sensitive=False),
              help='Technology stack of the project.')
@click.option('--project', 'project_name', help='(Optional) Project name to save results to.')
def scan(code_path: str, tech: str, project_name: Optional[str]):
    """Runs data-driven validation tools on a codebase."""
    click.echo(f"🔬 Scanning codebase at: {code_path}")
    
    results = run_scan(code_path, tech)
    
    click.echo("\n📊 SCAN SUMMARY:")
    for tool_name, result in results.items():
        if "error" in result:
            click.secho(f"  ❌ {tool_name}: {result['error']}", fg="red")
        else:
            click.secho(f"  ✅ {tool_name}: Success (exit code: {result['exit_code']})", fg="green")

    if project_name:
        try:
            output_dir = PROJECTS_DIR / project_name / "tool_outputs"
            output_dir.mkdir(exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = output_dir / f"scan_{tech}_{ts}.json"
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            click.echo(f"\n💾 Full results saved to: {output_file}")
            click.echo("\n📝 NEXT STEPS (HUMAN):")
            click.echo(f"1. Open the project's '03_data_driven_validation.md' file.")
            click.echo(f"2. Copy the relevant raw outputs from {output_file} into it.")
            click.echo(f"3. Write your analysis in the SUMMARY sections.")
        except Exception as e:
            click.echo(f"\n❌ Error saving results: {e}", err=True)
