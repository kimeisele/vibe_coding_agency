# Defines the validation tools for different technology stacks
TECH_STACK_TOOLS = {
    "python": {
        "linter": "flake8 . --max-complexity 10",
        "security": "bandit -r .",
        "dependencies": "pip-audit",
        "complexity": "radon cc . -a"
    },
    "javascript": {
        "linter": "npx eslint .",
        "security": "npm audit",
        "dependencies": "npm outdated"
    },
    "django": {
        "linter": "flake8 . --max-complexity 10",
        "security": "bandit -r .",
        "django_check": "python manage.py check --deploy"
    },
    "react": {
        "linter": "npx eslint src/",
        "security": "npm audit",
        "bundle_size": "npx webpack-bundle-analyzer"
    }
}
