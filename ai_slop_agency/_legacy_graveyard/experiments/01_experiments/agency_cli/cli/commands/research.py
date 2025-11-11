import click
from typing import Optional
from datetime import datetime

from core.researcher import get_research_queries
from config.settings import PROJECTS_DIR

@click.command()
@click.argument('query')
@click.option('--project', 'project_name', help='(Optional) Project name to save research plan to.')
def research(query: str, project_name: Optional[str]):
    """Suggests research queries for a given topic."""
    click.echo(f"🔍 Generating research plan for: '{query}'")
    
    queries = get_research_queries(query)
    
    click.echo("\nSuggested search queries:")
    for i, q in enumerate(queries, 1):
        click.echo(f"  {i}. {q}")
        
    click.echo("\n⚠️ IMPLEMENTATION NOTE:")
    click.echo("   This CLI does not run the web searches for you.")
    click.echo("   Your task is to run these searches and synthesize the results.")

    if project_name:
        try:
            results_path = PROJECTS_DIR / project_name / "research_results"
            results_path.mkdir(exist_ok=True)
            results_file = results_path / f"{query.replace(' ', '_')}_plan.md"
            
            # You can expand this to save a more detailed template
            plan_content = f"# Research Plan: {query}\n\n"
            plan_content += "\n".join(f"- [ ] {q}" for q in queries)
            results_file.write_text(plan_content)
            
            click.echo(f"\n📝 Research plan saved to: {results_file}")
        except Exception as e:
            click.echo(f"\n❌ Error saving research plan: {e}", err=True)
