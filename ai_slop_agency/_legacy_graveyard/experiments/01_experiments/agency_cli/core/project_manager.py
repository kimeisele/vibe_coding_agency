from pathlib import Path
from datetime import datetime

from config.settings import PROJECTS_DIR
from templates.loader import get_template, get_all_template_names

def create_project(project_name: str, client_input: str) -> Path:
    """
    Creates a new project workspace.
    
    - Creates the directory structure.
    - Populates it with protocol templates.
    
    Returns the path to the newly created project.
    Raises FileExistsError if project already exists.
    """
    project_path = PROJECTS_DIR / project_name
    
    if project_path.exists():
        raise FileExistsError(f"Project {project_name} already exists at {project_path}")

    # Create directory structure
    (project_path / "research_results").mkdir(parents=True)
    (project_path / "tool_outputs").mkdir(parents=True)
    (project_path / "reports").mkdir(parents=True)
    
    # Prepare context for templates
    context = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "project_name": project_name,
        "client_input": client_input
    }
    
    # Copy templates with filled context
    template_names = get_all_template_names()
    for template_name in template_names:
        file_path = project_path / template_name
        template_content = get_template(template_name)
        file_path.write_text(template_content.format(**context))
        
    return project_path
