# Universal Config

A professional-grade configuration system for any Python application. Stop managing environment variables manually - start using structured, validated configuration.

## Features

- **🏗️ Structured Configuration**: Organize settings with typed dataclasses
- **🌍 Environment Support**: Development, production, and test configurations
- **📝 YAML Files**: Human-readable configuration with environment variable substitution
- **✅ Validation**: Automatic validation with helpful error messages
- **🔧 Type Safety**: Full type hints and mypy compatibility
- **🎯 Zero Boilerplate**: Get started in seconds

## Installation

```bash
pip install universal-config
```

For development:
```bash
pip install universal-config[dev]
```

## Quick Start

### Basic Usage

```python
from phoenix_config import UniversalConfig

# Load from environment variables
config = UniversalConfig.load_from_env()

# Access configuration
print(f"Database URL: {config.database.url}")
print(f"API Port: {config.api.port}")
print(f"Log Level: {config.logging.level}")
```

### Environment-Specific Configs

```python
from pathlib import Path
from phoenix_config import UniversalConfig

# Development
dev_config = UniversalConfig.create_for_development(Path.cwd())
print(f"Debug mode: {dev_config.api.debug}")

# Production
prod_config = UniversalConfig.create_for_production()
print(f"Workers: {prod_config.api.workers}")

# Testing
test_config = UniversalConfig.create_for_testing()
print(f"Database: {test_config.database.url}")
```

### YAML Configuration

Create `config.yaml`:

```yaml
environment: development

database:
  url: "${DATABASE_URL}"
  pool_size: 10
  echo: true

api:
  host: "0.0.0.0"
  port: 8000
  debug: true
  workers: 1

logging:
  level: "DEBUG"
  format: "console"

performance:
  enable_caching: true
  max_concurrent_operations: 20
```

Load it:

```python
from phoenix_config import UniversalConfig

config = UniversalConfig.load_from_file("config.yaml")
print(f"Environment: {config.environment}")
```

## Configuration Components

### DatabaseConfig
```python
@dataclass
class DatabaseConfig:
    url: str = "sqlite:///app.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    auto_create_tables: bool = True
```

### APIConfig
```python
@dataclass
class APIConfig:
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    workers: int = 1
    reload: bool = False
```

### LoggingConfig
```python
@dataclass
class LoggingConfig:
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: str = "json"  # json, console, structured
    log_file: Optional[str] = None
```

### ShellConfig
```python
@dataclass
class ShellConfig:
    timeout: int = 60
    max_output_lines: int = 1000
    respect_gitignore: bool = True
```

## Environment Variables

The system automatically loads these environment variables:

```bash
# Core
APP_ENV=production
APP_PROJECT_ROOT=/path/to/project

# Database
DATABASE_URL=postgresql://user:pass@localhost/db
DB_POOL_SIZE=10
DB_ECHO=false

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
API_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/app.log

# Performance
ENABLE_CACHING=true
MAX_CONCURRENT=20

# Cache
CACHE_BACKEND=redis
CACHE_URL=redis://localhost:6379
CACHE_TTL=300
```

## Advanced Usage

### Custom Configuration

```python
from phoenix_config import UniversalConfig, DatabaseConfig, APIConfig

# Create custom config
config = UniversalConfig(
    environment="production",
    database=DatabaseConfig(
        url="postgresql://user:pass@localhost/prod",
        pool_size=20
    ),
    api=APIConfig(
        host="0.0.0.0",
        port=80,
        workers=8
    )
)

# Validate and save
config.validate()
config.save_to_file("production.yaml")
```

### Configuration Validation

```python
from phoenix_config import UniversalConfig, ConfigurationError

try:
    config = UniversalConfig.load_from_file("config.yaml")
except ConfigurationError as e:
    print(f"Configuration errors: {e.validation_errors}")
    print(f"Config file: {e.config_path}")
```

### Environment Detection

```python
config = UniversalConfig.load_from_env()

if config.is_production():
    # Production setup
    enable_monitoring()
elif config.is_development():
    # Development setup
    enable_debug_tools()
elif config.is_test():
    # Test setup
    use_test_database()
```

## Integration Examples

### FastAPI Application

```python
from fastapi import FastAPI
from phoenix_config import UniversalConfig

config = UniversalConfig.load_from_env()

app = FastAPI(
    debug=config.api.debug,
    host=config.api.host,
    port=config.api.port
)

@app.get("/config")
async def get_config():
    return {
        "environment": config.environment,
        "database_url": config.get_database_url(),
        "log_level": config.logging.level
    }
```

### SQLAlchemy Setup

```python
from sqlalchemy import create_engine
from phoenix_config import UniversalConfig

config = UniversalConfig.load_from_env()

engine = create_engine(
    config.get_database_url(),
    pool_size=config.database.pool_size,
    echo=config.database.echo
)
```

### Logging Configuration

```python
import logging
from phoenix_config import UniversalConfig

config = UniversalConfig.load_from_env()

# Configure logging based on config
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if config.logging.format == "console" else None
)

if config.logging.log_file:
    file_handler = logging.FileHandler(config.logging.log_file)
    logging.getLogger().addHandler(file_handler)
```

## API Reference

### UniversalConfig

Main configuration class with methods:

- `load_from_file(path)` - Load from YAML file
- `load_from_env()` - Load from environment variables
- `create_default()` - Default configuration
- `create_for_production()` - Production optimized
- `create_for_development(project_root)` - Development optimized
- `create_for_testing(**overrides)` - Testing optimized
- `validate()` - Validate configuration
- `save_to_file(path)` - Save to YAML file
- `to_dict()` - Convert to dictionary
- `get_database_url()` - Get database URL with env substitution
- `is_production()` - Check production mode
- `is_development()` - Check development mode
- `is_test()` - Check test mode

## Development

```bash
# Clone repository
git clone https://github.com/your-username/universal-config.git
cd universal-config

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run linting
black phoenix_config/
flake8 phoenix_config/
mypy phoenix_config/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Why Universal Config?

- **Stop the env-var chaos**: No more scattered `os.getenv()` calls
- **Type safety**: Catch configuration errors at runtime, not in production
- **Environment aware**: Different configs for dev, test, and prod
- **Validation**: Get helpful error messages, not cryptic failures
- **Zero dependencies**: Only PyYAML required
- **Battle-tested**: Based on production configuration system

Replace your configuration chaos with structured, validated settings today!
