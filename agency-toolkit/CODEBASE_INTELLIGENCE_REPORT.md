# Codebase Intelligence Report (Repo Map)

This document serves as the "Repo Map" for the Project Steward persona, providing a high-level overview of the `agency_toolkit` codebase structure, modules, classes, and functions.

```
FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/__init__.py
  (No classes or functions found)
  Imports:
    (No imports found)

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/cli_app.py
  Functions:
    - version_callback(value: bool) -> None
    - main(ctx: typer.Context, version: bool | None, verbose: bool, quiet: bool, output_dir: Path | None, json_output: bool, offline: bool) -> None
    - cli_entrypoint() -> None
  Imports:
    from pathlib import Path
    import typer
    from agency_toolkit import __version__
    from agency_toolkit.commands import ai_command, briefing_command, image_command, info_command, os_command, social_command, structure_command, validate_command
    from agency_toolkit.logger import setup_logging
    from agency_toolkit.utils import load_config

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/__init__.py
  (No classes or functions found)
  Imports:
    from agency_toolkit.commands.ai import ai_command
    from agency_toolkit.commands.briefing import briefing_command
    from agency_toolkit.commands.image import image_command
    from agency_toolkit.commands.info import info_command
    from agency_toolkit.commands.os import app as os_command
    from agency_toolkit.commands.social import social_command
    from agency_toolkit.commands.structure import structure_command
    from agency_toolkit.commands.validate import validate_command

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/ai.py
  Functions:
    - _load_profile(profile: str | None = None) -> dict
    - _load_prompt(prompt: str | None, prompt_file: Path | None, from_stdin: bool) -> str
    - ai(ctx: typer.Context, prompt: str | None, prompt_file: Path | None, stdin: bool, profile: str | None, provider: str, model: str | None, temperature: float, max_tokens: int, json_output_legacy: bool) -> None
  Imports:
    import json, logging, sys
    from pathlib import Path
    import httpx, typer
    from agency_toolkit.config import MISTRAL_PROFILES
    from agency_toolkit.exceptions import AIProviderError, ValidationError
    from agency_toolkit.providers import get_text_provider, list_text_providers

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/briefing.py
  Functions:
    - briefing(ctx: typer.Context, from_json: Path | None, briefing_type: str, format_type: str, dry_run: bool) -> None
  Imports:
    import json, logging
    from datetime import datetime
    from pathlib import Path
    import typer
    from agency_toolkit.core.briefing import BriefingData, collect_interactive, generate, load_briefing_questions, load_from_json

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/image.py
  Functions:
    - image(ctx: typer.Context, prompt: str, seed: int | None, width: int, height: int, provider: str) -> None
  Imports:
    import json, logging, typer
    from agency_toolkit import image_gen

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/info.py
  Functions:
    - get_available_social_templates() -> dict[str, str]
    - get_available_seed_templates() -> dict[str, str]
    - get_available_providers() -> dict[str, dict]
    - load_toolkit_docs() -> str
    - _display_commands_section(reporter=None) -> None
    - _display_social_templates_section(reporter=None) -> None
    - _display_image_providers_section(reporter=None) -> None
    - _display_seed_templates_section(reporter=None) -> None
    - _display_help_section(reporter=None) -> None
    - info(ctx: typer.Context) -> None
    - ask(ctx: typer.Context, query: str) -> None
    - _get_text_providers()
    - _get_image_providers()
    - _check_text_provider_status(provider_name: str, env_var: str) -> tuple[str, str]
    - _check_image_provider_status(provider_name: str, env_var: str, note: str) -> tuple[str, str]
    - _create_providers_table()
    - _calculate_provider_counts() -> tuple[int, int]
    - _print_summary_message(configured_count: int, total_required: int) -> None
    - _display_providers_header(reporter=None) -> None
    - _display_providers_table(reporter=None) -> None
    - _display_providers_summary(reporter=None) -> None
    - providers_status(ctx: typer.Context) -> None
  Imports:
    import json, logging, time
    from pathlib import Path
    import typer
    from agency_toolkit.core.reporter import get_reporter
    from agency_toolkit.providers.mistral_provider import MistralProvider

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/interactive_utils.py
  Functions:
    - prompt_for_social_post() -> dict
    - prompt_for_briefing_type() -> str
    - prompt_for_structure_type() -> str
    - confirm_action(message: str = "Proceed?") -> bool
    - display_summary(title: str, items: dict[str, str]) -> None
    - prompt_with_fallback(prompt_text: str, interactive: bool, default: str) -> str
    - prompt_for_selection(prompt_text: str, choices: list[dict], id_key: str, name_key: str, description_key: str) -> dict
  Imports:
    import questionary
    from agency_toolkit.config import COLORS
    from agency_toolkit.core.discovery import get_available_briefing_types, get_available_social_formats, get_available_social_styles, get_available_structure_types, get_choice_list, get_seed_choice_list

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/os.py
  Functions:
    - _validate_scenario(scenario: dict, idx: int) -> tuple[bool, dict | None]
    - _execute_single_scenario(scenario: dict, idx: int) -> dict
    - _display_batch_summary(results_summary: list[dict], reporter=None) -> None
    - os_init(ctx: typer.Context, name: str | None, from_csv: Path | None, from_json: Path | None, dry_run: bool) -> None
    - _batch_process_csv(csv_path: Path, reporter=None) -> None
    - _batch_process_json(json_path: Path, reporter=None) -> None
    - _process_batch_scenario(scenario: dict, idx: int, total: int, reporter=None) -> dict
    - _execute_batch(scenarios: list[dict], reporter=None) -> None
  Imports:
    import csv, json
    from pathlib import Path
    import typer
    from rich.console import Console
    from rich.table import Table
    from agency_toolkit.core.os_executor import execute_project_workflow
    from agency_toolkit.core.os_interactive import run_interactive_workflow
    from agency_toolkit.core.reporter import get_reporter
    from agency_toolkit.core.workflow_loader import validate_registry

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/social.py
  Functions:
    - _validate_social_arguments(text: str | None, from_csv: Path | None, from_json: Path | None) -> None
    - _validate_batch_file_exclusivity(from_csv: Path | None, from_json: Path | None, reporter) -> None
    - _validate_text_batch_exclusivity(text: str | None, from_csv: Path | None, from_json: Path | None, reporter) -> None
    - _validate_at_least_one_input(text: str | None, from_csv: Path | None, from_json: Path | None, reporter) -> None
    - _determine_processing_mode(text: str | None, from_csv: Path | None, from_json: Path | None) -> str
    - _handle_social_error(config, error: Exception, reporter: Reporter) -> None
    - social(ctx: typer.Context, text: str | None, style: str, color: str, custom_color: str | None, format_type: str, bg_concept: str | None, bg_seed: int | None, output_path: Path | None, dry_run: bool, from_csv: Path | None, from_json: Path | None) -> None
    - _handle_single_post(config, text, style, color, custom_color, format_type, bg_concept, bg_seed, output_path, dry_run, reporter: Reporter)
    - _handle_batch_csv(config, csv_path, output_path, dry_run, reporter: Reporter)
    - _handle_batch_json(config, json_path, output_path, dry_run, reporter: Reporter)
    - _display_batch_results(config, result, dry_run, reporter: Reporter)
  Imports:
    import logging
    from pathlib import Path
    import typer
    from agency_toolkit.core.reporter import Reporter, get_reporter
    from agency_toolkit.core.social import generate as generate_social_post, generate_background, process_batch_csv, process_batch_json

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/structure.py
  Functions:
    - structure(ctx: typer.Context, client: str, project: str, type_name: str, base_path: Path | None, dry_run: bool, force: bool) -> None
  Imports:
    import json, logging
    from pathlib import Path
    import typer
    from agency_toolkit.core.structure import generate

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/validate.py
  Functions:
    - _hash_file(file_path: Path) -> str
    - _extract_pdf_text(pdf_path: Path, reporter=None) -> str
    - _compare_pdf_files(current_file: Path, approved_file: Path, filename: str, reporter=None) -> dict
    - _compare_image_files(current_file: Path, approved_file: Path, filename: str, reporter=None) -> dict
    - _compare_json_files(current_file: Path, approved_file: Path, filename: str, reporter=None) -> dict
    - _compare_generic_files(current_file: Path, approved_file: Path, filename: str, reporter=None) -> dict
    - _get_file_comparator(filename: str)
    - _process_file_comparison(filename: str, current_files: dict, approved_files: dict, reporter=None) -> dict
    - _validate_snapshot_dirs(current_dir: Path, approved_dir: Path, reporter=None) -> bool
    - _collect_snapshot_files(current_dir: Path, approved_dir: Path) -> tuple[dict, dict, set]
    - _aggregate_comparison_results(results: list[dict]) -> dict
    - _compare_snapshots(current_dir: Path, approved_dir: Path, reporter=None) -> dict
    - snapshot_validate(ctx: typer.Context, approve: bool, generate: bool) -> None
  Imports:
    import hashlib, json, logging, shutil
    from pathlib import Path
    import typer
    from agency_toolkit.core.reporter import get_reporter

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/commands/validators.py
  Classes:
    - ValidationError(Exception)
  Functions:
    - validate_file_exists(file_path: Path | None, name: str) -> None
    - validate_directory_exists(dir_path: Path | None, name: str) -> None
    - validate_file_extension(file_path: Path, allowed_extensions: Set[str], name: str) -> None
    - validate_enum_choice(value: str, allowed_values: Set[str], name: str) -> None
    - validate_numerical_range(value: int | float, min_value: int | float | None, max_value: int | float | None, name: str) -> None
    - validate_mutually_exclusive(*args: Any, arg_names: list[str], name: str) -> None
    - validate_at_least_one(*args: Any, arg_names: list[str], name: str) -> None
    - validate_non_empty_string(value: str | None, name: str, allow_none: bool) -> None
    - handle_validation_error(error: ValidationError, reporter: Optional[Reporter]) -> None
  Imports:
    from pathlib import Path
    from typing import Any, Optional, Set
    import typer
    from agency_toolkit.core.reporter import Reporter, get_reporter

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/config.py
  (No classes or functions found)
  Imports:
    from pathlib import Path

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/constants.py
  (No classes or functions found)
  Imports:
    (No imports found)

FilePath: /Users/ss/projects/agency_toolkit/agency_toolkit/core/briefing/generator.py
  Functions:
    - generate(briefing_data: BriefingData, format_type: str, output_dir: Path, dry_run: bool, step_context: dict | None) -> dict
  Imports:
    import logging
    from datetime import datetime
    from pathlib import Path
    from agency_toolkit.core.briefing.io import write_markdown
    from agency_toolkit.core.briefing.models import BriefingData
    from agency_toolkit.core.briefing.pdf_writer import write_pdf
    from agency_toolkit.utils import ensure_output_dir, sanitize_name

...and so on for all 68 files.
```
