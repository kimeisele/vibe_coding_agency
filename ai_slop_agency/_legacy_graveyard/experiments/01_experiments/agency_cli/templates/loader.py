from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "files"

def get_template(name: str) -> str:
    """Loads a template file by name."""
    template_file = TEMPLATE_DIR / name
    if not template_file.exists():
        raise FileNotFoundError(f"Template {name} not found in {TEMPLATE_DIR}")
    return template_file.read_text()

def get_all_template_names() -> list[str]:
    """Returns a list of all available template filenames."""
    if not TEMPLATE_DIR.exists():
        return []
    return [f.name for f in TEMPLATE_DIR.iterdir() if f.is_file()]
