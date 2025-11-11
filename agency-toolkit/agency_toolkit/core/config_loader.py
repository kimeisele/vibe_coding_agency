"""Universal Config loader for Agency Toolkit.

Provides convenient access to configuration from UniversalConfig.
"""

from pathlib import Path

from agency_toolkit.core.phoenix_config import UniversalConfig

# Global config instance (lazy-loaded)
_config: UniversalConfig | None = None


def get_config() -> UniversalConfig:
    """Get or create the global UniversalConfig instance.

    Returns:
        Initialized UniversalConfig pointing to agency_toolkit/configs/
    """
    global _config
    if _config is None:
        # Try to load from config file, fall back to environment
        config_dir = Path(__file__).parent.parent / "configs"
        config_file = config_dir / "development.yaml"

        if config_file.exists():
            _config = UniversalConfig.load_from_file(str(config_file))
        else:
            _config = UniversalConfig.load_from_env()

    return _config


def reload_config() -> UniversalConfig:
    """Reload configuration from source (useful for testing).

    Returns:
        Reloaded UniversalConfig instance
    """
    global _config
    _config = None
    return get_config()


def get_database_config():
    """Get database configuration.

    Returns:
        DatabaseConfig object with database settings
    """
    return get_config().database


def get_api_config():
    """Get API configuration.

    Returns:
        APIConfig object with API server settings
    """
    return get_config().api


def get_logging_config():
    """Get logging configuration.

    Returns:
        LoggingConfig object with logging settings
    """
    return get_config().logging


def get_shell_config():
    """Get shell execution configuration.

    Returns:
        ShellConfig object with shell command settings
    """
    return get_config().shell


def get_cache_config():
    """Get cache configuration.

    Returns:
        CacheConfig object with cache backend settings
    """
    return get_config().cache


def get_environment() -> str:
    """Get current environment (development/production/test).

    Returns:
        Environment string
    """
    return get_config().environment


def is_production() -> bool:
    """Check if running in production environment.

    Returns:
        True if environment is production
    """
    return get_config().is_production()


def is_development() -> bool:
    """Check if running in development environment.

    Returns:
        True if environment is development
    """
    return get_config().is_development()


def is_test() -> bool:
    """Check if running in test environment.

    Returns:
        True if environment is test
    """
    return get_config().is_test()
