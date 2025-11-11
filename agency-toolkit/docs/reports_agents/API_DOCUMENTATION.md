# API Documentation - Refactored Modules

This document provides comprehensive API documentation for the refactored validate.py and os.py modules, as well as the Reporter module.

## Table of Contents

- [Reporter Module](#reporter-module)
- [Validate Module](#validate-module)
- [OS Module](#os-module)
- [Info Module](#info-module)
- [Social Module](#social-module)

---

## Reporter Module

### Overview

The `Reporter` module provides consistent CLI output formatting across all agency toolkit commands. It supports both human-readable and JSON output formats.

### Location
`agency_toolkit/core/reporter.py`

### Classes

#### `Reporter`

The main reporter class that handles all CLI output formatting.

##### Constructor

```python
def __init__(self, json_output: bool = False)
```

**Parameters:**
- `json_output` (bool): If True, output will be formatted as JSON. Default: False

##### Methods

###### `success(message: str, exit_code: int = 1) -> None`
Display success message in green.

**Parameters:**
- `message` (str): Success message to display
- `exit_code` (int): Exit code (default: 1, but typically 0 for success)

###### `error(message: str, exit_code: int = 1) -> None`
Display error message in red and exit.

**Parameters:**
- `message` (str): Error message to display
- `exit_code` (int): Exit code (default: 1)

###### `warning(message: str) -> None`
Display warning message in yellow.

**Parameters:**
- `message` (str): Warning message to display

###### `info(message: str, data: dict = None) -> None`
Display informational message.

**Parameters:**
- `message` (str): Info message to display
- `data` (dict, optional): Additional data to include in JSON output

###### `processing(message: str) -> None`
Display processing/working message.

**Parameters:**
- `message` (str): Processing message to display

###### `validation_result(filename: str, passed: bool, details: str) -> None`
Display validation result for a file.

**Parameters:**
- `filename` (str): Name of the file being validated
- `passed` (bool): Whether validation passed
- `details` (str): Additional details about the validation

###### `divider(width: int = 60) -> None`
Display divider line.

**Parameters:**
- `width` (int): Width of the divider (default: 60)

##### Usage Example

```python
from agency_toolkit.core.reporter import get_reporter

# Get reporter instance
reporter = get_reporter(json_output=False)

# Use reporter methods
reporter.success("Operation completed successfully")
reporter.error("Something went wrong", exit_code=1)
reporter.warning("This is a warning")
reporter.info("Processing file...")
reporter.validation_result("test.txt", True, "hash match")
reporter.divider()
```

#### Global Functions

##### `get_reporter(json_output: bool = False) -> Reporter`
Get a reporter instance.

**Parameters:**
- `json_output` (bool): Whether to output in JSON format

**Returns:**
- `Reporter`: Reporter instance

---

## Validate Module

### Overview

The validate module provides snapshot validation and regression testing functionality. It has been refactored to reduce cyclomatic complexity and improve maintainability.

### Location
`agency_toolkit/commands/validate.py`

### Refactored Functions

#### File Comparison Functions

##### `_compare_pdf_files(current_file: Path, approved_file: Path, filename: str, reporter=None) -> dict`
Compare two PDF files by text content.

**Parameters:**
- `current_file` (Path): Path to current PDF file
- `approved_file` (Path): Path to approved PDF file
- `filename` (str): Name of the file for reporting
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `dict`: Result with 'passed' boolean and optional 'difference' info

##### `_compare_image_files(current_file: Path, approved_file: Path, filename: str, reporter=None) -> dict`
Compare two image files by hash.

**Parameters:**
- `current_file` (Path): Path to current image file
- `approved_file` (Path): Path to approved image file
- `filename` (str): Name of the file for reporting
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `dict`: Result with 'passed' boolean and optional 'difference' info

##### `_compare_json_files(current_file: Path, approved_file: Path, filename: str, reporter=None) -> dict`
Compare two JSON files by content.

**Parameters:**
- `current_file` (Path): Path to current JSON file
- `approved_file` (Path): Path to approved JSON file
- `filename` (str): Name of the file for reporting
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `dict`: Result with 'passed' boolean and optional 'difference' info

##### `_compare_generic_files(current_file: Path, approved_file: Path, filename: str, reporter=None) -> dict`
Compare two files by hash (fallback for unknown file types).

**Parameters:**
- `current_file` (Path): Path to current file
- `approved_file` (Path): Path to approved file
- `filename` (str): Name of the file for reporting
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `dict`: Result with 'passed' boolean and optional 'difference' info

#### Utility Functions

##### `_get_file_comparator(filename: str) -> callable`
Get the appropriate comparator function for a file type.

**Parameters:**
- `filename` (str): Name of file to compare

**Returns:**
- `callable`: Comparator function

##### `_hash_file(file_path: Path) -> str`
Calculate SHA-256 hash of file.

**Parameters:**
- `file_path` (Path): Path to file to hash

**Returns:**
- `str`: SHA-256 hash as hex string

##### `_extract_pdf_text(pdf_path: Path, reporter=None) -> str`
Extract text from PDF for comparison.

**Parameters:**
- `pdf_path` (Path): Path to PDF file
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `str`: Extracted text content

#### Orchestration Functions

##### `_process_file_comparison(filename: str, current_files: dict, approved_files: dict, reporter=None) -> dict`
Process a single file comparison.

**Parameters:**
- `filename` (str): Name of file to compare
- `current_files` (dict): Mapping of current files
- `approved_files` (dict): Mapping of approved files
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `dict`: Result with 'passed', 'status', and optional 'difference'

##### `_validate_snapshot_dirs(current_dir: Path, approved_dir: Path, reporter=None) -> bool`
Check if snapshot directories exist.

**Parameters:**
- `current_dir` (Path): Current snapshot directory
- `approved_dir` (Path): Approved snapshot directory
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `bool`: True if both directories exist and are valid

##### `_collect_snapshot_files(current_dir: Path, approved_dir: Path) -> tuple[dict, dict, set]`
Collect and organize snapshot files from both directories.

**Parameters:**
- `current_dir` (Path): Current snapshot directory
- `approved_dir` (Path): Approved snapshot directory

**Returns:**
- `tuple`: (current_files, approved_files, all_filenames)

##### `_aggregate_comparison_results(results: list[dict]) -> dict`
Aggregate results from individual file comparisons.

**Parameters:**
- `results` (list): List of comparison result dictionaries

**Returns:**
- `dict`: Aggregated results with counts and differences

##### `_compare_snapshots(current_dir: Path, approved_dir: Path, reporter=None) -> dict`
Compare current snapshots against approved (main orchestrator).

**Parameters:**
- `current_dir` (Path): Current snapshot directory
- `approved_dir` (Path): Approved snapshot directory
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `dict`: Results with total, passed, failed, missing counts and differences list

#### CLI Command

##### `snapshot_validate(ctx: typer.Context, approve: bool = False, generate: bool = False) -> None`
Validate outputs against approved snapshots.

**Parameters:**
- `ctx` (typer.Context): Typer context containing config
- `approve` (bool): Approve current snapshots as new baseline
- `generate` (bool): Generate snapshots before validation

---

## OS Module

### Overview

The OS module provides GRAND AGENCY OS commands for orchestrated project workflows. It has been refactored to reduce cyclomatic complexity and improve batch processing functionality.

### Location
`agency_toolkit/commands/os.py`

### Refactored Functions

#### Validation Functions

##### `_validate_scenario(scenario: dict, idx: int) -> tuple[bool, dict | None]`
Validate a single scenario for required fields.

**Parameters:**
- `scenario` (dict): Scenario dictionary to validate
- `idx` (int): Scenario index (for reporting)

**Returns:**
- `tuple`: (is_valid, error_dict or None)

#### Batch Processing Functions

##### `_process_batch_scenario(scenario: dict, idx: int, total: int, reporter=None) -> dict`
Process a single scenario in batch mode.

**Parameters:**
- `scenario` (dict): Scenario dictionary to process
- `idx` (int): Scenario index (for reporting)
- `total` (int): Total number of scenarios
- `reporter` (Reporter, optional): Reporter instance for output

**Returns:**
- `dict`: Result dictionary with status and details

##### `_execute_batch(scenarios: list[dict], reporter=None) -> None`
Execute batch of scenarios (orchestrator function).

**Parameters:**
- `scenarios` (list): List of scenario dictionaries
- `reporter` (Reporter, optional): Reporter instance for output

##### `_display_batch_summary(results_summary: list[dict], reporter=None) -> None`
Display batch execution summary table and stats.

**Parameters:**
- `results_summary` (list): List of result dictionaries
- `reporter` (Reporter, optional): Reporter instance for output

##### `_batch_process_csv(csv_path: Path, reporter=None) -> None`
Process multiple projects from CSV file.

**Parameters:**
- `csv_path` (Path): Path to CSV file
- `reporter` (Reporter, optional): Reporter instance for output

**CSV Format:**
```
project_name,archetype_id,solution_id,module_id,ai_provider
```

##### `_batch_process_json(json_path: Path, reporter=None) -> None`
Process multiple projects from JSON file.

**Parameters:**
- `json_path` (Path): Path to JSON file
- `reporter` (Reporter, optional): Reporter instance for output

**JSON Format:**
```json
[
    {
        "project_name": "Test1",
        "archetype_id": "archetype-i",
        "solution_id": "solution-a1",
        "module_id": "mod-a1-4-recruiting",
        "ai_provider": "google"  // optional
    }
]
```

#### CLI Command

##### `os_init(ctx: typer.Context, name: str | None = None, from_csv: Path | None = None, from_json: Path | None = None, dry_run: bool = False) -> None`
Initialize GRAND AGENCY project(s) with guided or batch workflow.

**Parameters:**
- `ctx` (typer.Context): Typer context containing config
- `name` (str, optional): Project name (for single execution)
- `from_csv` (Path, optional): Batch process from CSV file
- `from_json` (Path, optional): Batch process from JSON file
- `dry_run` (bool): Show execution plan without running tasks

**Modes:**
- Interactive (default): Guided workflow with prompts
- Single: Provide --name with flags
- Batch CSV: Process multiple projects from CSV
- Batch JSON: Process multiple projects from JSON

---

## Usage Examples

### Validate Module

```python
from agency_toolkit.commands.validate import _compare_snapshots
from agency_toolkit.core.reporter import get_reporter
from pathlib import Path

# Compare snapshots
reporter = get_reporter()
current_dir = Path("snapshots/current")
approved_dir = Path("snapshots/approved")

results = _compare_snapshots(current_dir, approved_dir, reporter)
print(f"Total: {results['total']}, Passed: {results['passed']}")
```

### OS Module

```python
from agency_toolkit.commands.os import _execute_batch
from agency_toolkit.core.reporter import get_reporter

# Execute batch scenarios
scenarios = [
    {
        "project_name": "Test Project",
        "archetype_id": "I",
        "solution_id": "solution-a1",
        "module_id": "mod-a1-4-recruiting"
    }
]

reporter = get_reporter()
_execute_batch(scenarios, reporter)
```

### Reporter Module

```python
from agency_toolkit.core.reporter import get_reporter

# Human-readable output
reporter = get_reporter(json_output=False)
reporter.success("Operation completed")
reporter.error("Failed to process", exit_code=1)

# JSON output
reporter = get_reporter(json_output=True)
reporter.success("Operation completed")
# Output: {"status": "success", "message": "Operation completed"}
```

---

## Testing

The refactored modules include comprehensive unit tests:

- `tests/unit/test_validate_refactored_unit.py` - Tests for validate module functions
- `tests/unit/test_os_refactored_unit.py` - Tests for OS module functions

Run tests with:
```bash
python -m pytest tests/unit/test_validate_refactored_unit.py tests/unit/test_os_refactored_unit.py -v
```

---

## Info Module

### Overview

The `info` module provides comprehensive system information display capabilities including provider status, available templates, and help documentation. All functions have been refactored to support the Reporter pattern for consistent output formatting.

### Location
`agency_toolkit/commands/info.py`

### Public Functions

#### `providers_status(reporter: Optional[Reporter] = None) -> None`
Display comprehensive status of all configured providers (text and image).

**Parameters:**
- `reporter` (Optional[Reporter]): Reporter instance for output formatting

**Features:**
- Displays provider configuration status in a formatted table
- Shows summary of configured vs total providers
- Supports JSON output format

#### `info(reporter: Optional[Reporter] = None) -> None`
Display comprehensive system information including providers, commands, and templates.

**Parameters:**
- `reporter` (Optional[Reporter]): Reporter instance for output formatting

**Features:**
- Shows provider status
- Lists available commands
- Displays social media templates
- Shows image providers
- Lists seed templates
- Provides help information

#### `ask(reporter: Optional[Reporter] = None) -> None`
Display interactive help and documentation information.

**Parameters:**
- `reporter` (Optional[Reporter]): Reporter instance for output formatting

**Features:**
- Shows toolkit documentation
- Provides help context
- Displays cache information

### Internal Helper Functions

#### Provider Status Functions
- `_get_text_providers() -> List[str]` - Get available text providers
- `_get_image_providers() -> List[str]` - Get available image providers
- `_check_text_provider_status(provider: str) -> str` - Check text provider configuration
- `_check_image_provider_status(provider: str) -> str` - Check image provider configuration
- `_calculate_provider_counts() -> Tuple[int, int]` - Calculate configured/total counts
- `_create_providers_table() -> Table` - Create providers status table

#### Display Functions
- `_display_providers_header(reporter: Reporter) -> None` - Display providers section header
- `_display_providers_table(reporter: Reporter, table: Table) -> None` - Display providers table
- `_display_providers_summary(reporter: Reporter, configured: int, total: int) -> None` - Display summary
- `_display_commands_section(reporter: Reporter) -> None` - Display available commands
- `_display_social_templates_section(reporter: Reporter) -> None` - Display social templates
- `_display_image_providers_section(reporter: Reporter) -> None` - Display image providers
- `_display_seed_templates_section(reporter: Reporter) -> None` - Display seed templates
- `_display_help_section(reporter: Reporter) -> None` - Display help information

#### Utility Functions
- `get_available_social_templates() -> Dict[str, str]` - Get social media templates
- `get_available_seed_templates() -> Dict[str, str]` - Get seed templates
- `load_toolkit_docs() -> str` - Load toolkit documentation

### Usage Examples

#### Basic Provider Status
```python
from agency_toolkit.commands.info import providers_status
from agency_toolkit.core.reporter import Reporter

# Human-readable output
providers_status()

# JSON output
reporter = Reporter(json_output=True)
providers_status(reporter)
```

#### System Information
```python
from agency_toolkit.commands.info import info

# Display full system information
info()
```

#### Custom Reporter Integration
```python
from agency_toolkit.commands.info import providers_status
from agency_toolkit.core.reporter import Reporter

# Use custom reporter
reporter = Reporter(json_output=False)
providers_status(reporter)
```

### Testing

Run tests with:
```bash
python -m pytest tests/unit/test_info_refactored_unit.py -v
```

---

## Social Module

### Overview

The `social` module provides social media post generation capabilities with support for single posts and batch processing. The validation functions have been refactored to reduce complexity and improve maintainability, with full Reporter integration for consistent output formatting.

### Location
`agency_toolkit/commands/social.py`

### Public Functions

#### `social(ctx: typer.Context, ..., reporter: Optional[Reporter] = None) -> None`
Generate social media post image with optional AI background.

**Parameters:**
- `ctx` (typer.Context): Typer context containing configuration
- `text` (str | None): Main text content for the post
- `style` (str): Template style (default: "modern")
- `color` (str): Color or 'custom' (default: "blue")
- `custom_color` (str | None): Hex color if color=custom
- `format_type` (str): Image format (default: "square")
- `bg_concept` (str | None): Background concept (e.g., 'moody', 'registry:moody')
- `bg_seed` (int | None): Fixed seed for reproducible background
- `output_path` (Path | None): Custom output path
- `dry_run` (bool): Preview without saving (default: False)
- `from_csv` (Path | None): Generate posts from CSV file
- `from_json` (Path | None): Generate posts from JSON file
- `reporter` (Optional[Reporter]): Reporter instance for output formatting

**Features:**
- Single post generation with customizable styling
- AI background generation support
- Batch processing from CSV/JSON files
- Comprehensive argument validation
- Full Reporter integration for consistent output

### Internal Helper Functions

#### Validation Functions
- `_validate_social_arguments(text, from_csv, from_json) -> None` - Main validation orchestrator
- `_validate_batch_file_exclusivity(from_csv, from_json, reporter) -> None` - Validate batch file exclusivity
- `_validate_text_batch_exclusivity(text, from_csv, from_json, reporter) -> None` - Validate text/batch exclusivity
- `_validate_at_least_one_input(text, from_csv, from_json, reporter) -> None` - Validate input presence

#### Processing Functions
- `_determine_processing_mode(text, from_csv, from_json) -> str` - Determine processing mode
- `_handle_single_post(..., reporter) -> None` - Handle single post generation
- `_handle_batch_csv(..., reporter) -> None` - Handle CSV batch processing
- `_handle_batch_json(..., reporter) -> None` - Handle JSON batch processing
- `_display_batch_results(..., reporter) -> None` - Display batch results

#### Utility Functions
- `_handle_social_error(config, error, reporter) -> None` - Handle and display errors

### Usage Examples

#### Single Post Generation
```python
from agency_toolkit.commands.social import social
from agency_toolkit.core.reporter import Reporter
from unittest.mock import Mock

# Mock typer context
ctx = Mock()
ctx.obj = config

# Generate single post
social(
    ctx=ctx,
    text="Hello World!",
    style="modern",
    color="blue",
    reporter=Reporter()
)
```

#### Batch Processing
```python
# Process CSV file
social(
    ctx=ctx,
    from_csv=Path("campaign.csv"),
    output_path=Path("output"),
    dry_run=False,
    reporter=Reporter()
)
```

#### Custom Reporter Integration
```python
# Use custom reporter with JSON output
reporter = Reporter(json_output=True)
social(
    ctx=ctx,
    text="Test post",
    bg_concept="moody",
    reporter=reporter
)
```

### Complexity Improvements

The refactoring reduced cyclomatic complexity significantly:
- `_validate_social_arguments`: CC 9 → CC 1
- Split into 3 focused validation functions (CC 3-4 each)
- All functions now have CC < 10

### Testing

Run tests with:
```bash
python -m pytest tests/unit/test_social_refactored_unit.py -v
```

**Test Coverage:**
- 23 comprehensive unit tests
- All validation functions tested
- Error handling scenarios covered
- Integration tests for complete workflows

---

## Migration Guide

### From Old to New API

1. **Reporter Integration**: All functions now accept an optional `reporter` parameter
2. **Function Splitting**: Large functions have been split into smaller, focused functions
3. **Consistent Return Types**: All functions return consistent dictionary structures
4. **Error Handling**: Improved error handling with proper reporter integration

### Backward Compatibility

All public APIs remain backward compatible. The refactoring primarily affects internal function structure and adds optional reporter parameters for better testability.
